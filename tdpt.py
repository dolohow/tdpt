import time
import threading
import subprocess
import configparser

import telegram
import transmissionrpc

CONFIG = configparser.ConfigParser()
CONFIG.read('tdpt.ini')

TRANSMISSION = transmissionrpc.Client(CONFIG['Transmission']['host'],
                                      port=CONFIG['Transmission']['port'])
BOT = telegram.Bot(CONFIG['Telegram']['bot_token'])

def format_speed(speed):
    speed = float(speed)
    if speed < 1000000:
        return '{:.1f} {}'.format(speed/1000, 'kB/s')
    return '{:.1f} {}'.format(speed/1000/1000, 'MB/s')


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
            print('Creating new download message')
            self.message_id = self.bot.sendMessage(self.chat_id, self._get_new_text(),
                                                   parse_mode='markdown').message_id
        except telegram.error.TimedOut:
            print("Timeout")

    def update(self):
        self.torrent = TRANSMISSION.get_torrent(self.torrent.id)
        try:
            self.bot.editMessageText(self._get_new_text(), chat_id=self.chat_id,
                                     message_id=self.message_id, parse_mode='markdown')
        except telegram.error.BadRequest as bad_request:
            print(bad_request)
        except telegram.error.TimedOut:
            print("Timeout")

    def delete(self):
        self.bot.deleteMessage(chat_id=self.chat_id, message_id=self.message_id)

    def _get_new_text(self):
        return self.text.format(self.torrent.name, self.torrent.percentDone,
                                format_speed(self.torrent.rateDownload), self.torrent.format_eta(),
                                self.torrent.peersConnected)


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
    def cleanup(text):
        print(text)
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
            cleanup('Torrent removed')
            return
        if message.torrent.percentDone == 1.0:
            cleanup('Removing torrent from tracked')
            if not CONFIG.get('General', 'call_on_finish', fallback=None):
                return
            subprocess.Popen('notification', env={
                'TORRENT_NAME': message.torrent.name, 'LC_ALL': 'en_GB.UTF-8', 'LANG': 'en_GB.UTF-8'
            })

def main():
    torrents_tracked = set()
    time_counter = TimeCounter()
    while True:
        for torrent in TRANSMISSION.get_torrents():
            if torrent.id not in torrents_tracked and torrent.status == 'downloading':
                torrents_tracked.add(torrent.id)
                threading.Thread(target=handle_torrent,
                                 args=(torrent, time_counter, torrents_tracked)).start()

        time.sleep(10)

if __name__ == '__main__':
    main()
