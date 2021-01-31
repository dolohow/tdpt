import configparser
import importlib
import logging
import time

import telegram

from telegram.ext import Updater
from telegram.utils.helpers import escape_markdown

from handlers.message_handlers import UploadNewTorrent
from helpers import format_speed

CONFIG = configparser.ConfigParser()
CONFIG.read('tdpt.ini')

BOT = telegram.Bot(CONFIG['Telegram']['bot_token'])


class TorrentStatusMessage:
    text = ("""{}
```
Progress: {:.0%}
Speed:    {}
ETA:      {}
Peers:    {}

```""")

    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.message_id = None

    def create_or_update(self, torrents):
        if not self.message_id:
            self._create(torrents)
        else:
            self._update(torrents)

    def delete(self):
        self.bot.delete_message(chat_id=self.chat_id,
                                message_id=self.message_id)

    def _create(self, torrents):
        logging.info('Creating new download message')
        try:
            self.message_id = self.bot.send_message(
                self.chat_id,
                self._get_new_text(torrents),
                disable_notification=True,
                parse_mode='markdown').message_id
        except telegram.error.TimedOut:
            logging.warning("Timeout when creating a new download message")

    def _update(self, torrents):
        logging.info('Updating download message')
        try:
            self.bot.edit_message_text(self._get_new_text(torrents),
                                       chat_id=self.chat_id,
                                       message_id=self.message_id,
                                       parse_mode="markdown")
        except telegram.error.BadRequest as bad_request:
            if bad_request.message == 'Message to edit not found':
                self.message_id = None
                self._create(torrents)
            logging.warning(bad_request)
        except telegram.error.TimedOut:
            logging.warning('Timeout when editing message')

    def _get_new_text(self, torrents):
        msg = ""
        for torrent in torrents:
            name = escape_markdown(torrent.name)
            msg += self.text.format(name, torrent.percent_done,
                                    format_speed(torrent.download_rate),
                                    torrent.eta, torrent.peers_connected)
        return msg


def init_polling(client):
    updater = Updater(token=CONFIG['Telegram']['bot_token'], use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(UploadNewTorrent(client))
    updater.start_polling()


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
    backend_name = CONFIG.get('General', 'backend')

    backend = importlib.import_module('backends.' + backend_name.lower())
    client = backend.Client(CONFIG[backend_name])

    init_polling(client)
    message = TorrentStatusMessage(BOT, CONFIG['Telegram']['chat_id'])

    while True:
        prev_torrents_number = 0
        torrents = []
        for torrent in client.get_torrents():
            if torrent.is_downloading():
                torrents.append(torrent)

        if prev_torrents_number != len(torrents):
            message.create_or_update(torrents)
            prev_torrents_number = len(torrents)
        else:
            message.delete()

        time.sleep(3)


if __name__ == '__main__':
    main()
