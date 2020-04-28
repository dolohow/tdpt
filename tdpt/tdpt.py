import configparser
import importlib
import logging
import subprocess
import threading
import time

import telegram

from telegram.ext import Updater
from telegram.utils.helpers import escape_markdown

from tdpt.handlers.message_handlers import UploadNewTorrent
from tdpt.helpers import format_speed

CONFIG = configparser.ConfigParser()
CONFIG.read('tdpt.ini')

BOT = telegram.Bot(CONFIG['Telegram']['bot_token'])


class MessageNotFound(telegram.error.BadRequest):
    pass


class TorrentStatusMessage:
    text = (
"""{}

```
Progress: {:.0%}
Speed:    {}
ETA:      {}
Peers:    {}
```"""
    )

    def __init__(self, bot, chat_id, torrent):
        self.bot = bot
        self.torrent = torrent
        self.chat_id = chat_id
        self.message_id = None

    def create(self):
        try:
            logging.info('Creating new download message')
            self.message_id = self.bot.sendMessage(
                self.chat_id,
                self._get_new_text(),
                disable_notification=True,
                parse_mode='markdown').message_id
        except telegram.error.TimedOut:
            logging.warning("Timeout")

    def update(self):
        self.torrent.update()
        try:
            self.bot.editMessageText(self._get_new_text(),
                                     chat_id=self.chat_id,
                                     message_id=self.message_id,
                                     parse_mode='markdown')
        except telegram.error.BadRequest as bad_request:
            if bad_request.message == 'Message to edit not found':
                raise MessageNotFound(bad_request.message)
            logging.warning(bad_request)
        except telegram.error.TimedOut:
            logging.warning('Timeout when editing message')

    def delete(self):
        self.bot.deleteMessage(chat_id=self.chat_id,
                               message_id=self.message_id)

    def _get_new_text(self):
        name = escape_markdown(self.torrent.name)
        return self.text.format(name, self.torrent.percent_done,
                                format_speed(self.torrent.download_rate),
                                self.torrent.eta,
                                self.torrent.peers_connected)


class TimeCounter:

    messages_per_second = 3

    def __init__(self):
        self.counter = 0
        self.lock = threading.Lock()

    def next(self):
        with self.lock:
            self.counter += 1

    def prev(self):
        with self.lock:
            self.counter -= 1

    def get_time(self):
        return self.messages_per_second*self.counter+1


def handle_torrent(torrent, time_counter, torrents_tracked):

    def cleanup():
        message.delete()
        time_counter.prev()
        torrents_tracked.remove(torrent.id)

    message = TorrentStatusMessage(BOT, CONFIG['Telegram']['chat_id'], torrent)
    time_counter.next()
    message.create()
    while True:
        time.sleep(time_counter.get_time())
        try:
            message.update()
        except KeyError:
            cleanup()
            logging.info('Torrent removed')
            return
        except MessageNotFound as message_not_found:
            logging.warning(message_not_found)
            message.create()
            return
        if not message.torrent.is_downloading():
            cleanup()
            logging.info('Removing torrent from tracked')
            call_on_finish = CONFIG.get('General', 'call_on_finish',
                                        fallback=None)
            if not call_on_finish:
                return
            subprocess.Popen(call_on_finish, env={
                'TORRENT_NAME': message.torrent.name,
                'LC_ALL': 'en_GB.UTF-8',
                'LANG': 'en_GB.UTF-8',
            })
            return


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
    torrents_tracked = set()
    time_counter = TimeCounter()
    while True:
        for torrent in client.get_torrents():
            if (torrent.id not in torrents_tracked and
                    torrent.is_downloading()):
                torrents_tracked.add(torrent.id)
                threading.Thread(target=handle_torrent,
                                 args=(torrent,
                                       time_counter,
                                       torrents_tracked)).start()

        time.sleep(20)


if __name__ == '__main__':
    main()
