import base64
import datetime

from deluge_client import DelugeRPCClient


class Client:
    def __init__(self, config):
        self.client = DelugeRPCClient(config['host'], int(config['port']),
                                      config['username'], config['password'])

    def add_torrent(self, file_name, torrent, timeout=None, **kwargs):
        barray = torrent.download_as_bytearray()
        filedump = base64.b64encode(barray).decode('utf-8')
        self.client.core.add_torrent_file(file_name, filedump, timeout,
                                          **kwargs)

    def get_torrents(self):
        """Yields Torrents objects."""
        yield from map(lambda torrent: Torrent(torrent, self.client),
                       self.client.core.get_torrents_status({"state": "Downloading"}, ()))


class Torrent:

    PROPERTIES = ('name', 'state', 'hash', 'progress', 'eta', 'peers',
                  'download_payload_rate')

    def __init__(self, torrent_hash, client):
        self.torrent = None
        self.client = client
        self.update(torrent_hash)

    def is_downloading(self) -> bool:
        return self.torrent[b'state'] == b'Downloading'

    def update(self, torrent_hash=None):
        h = torrent_hash if torrent_hash else self.torrent[b'hash']
        self.torrent = self.client.core.get_torrent_status(h, self.PROPERTIES)

    @property
    def download_rate(self) -> int:
        return self.torrent[b'download_payload_rate']

    @property
    def eta(self):
        return datetime.timedelta(seconds=self.torrent[b'eta'])

    @property
    def id(self):
        return self.torrent[b'hash']

    @property
    def name(self):
        return str(self.torrent[b'name'], 'utf-8')

    @property
    def peers_connected(self):
        return len(self.torrent[b'peers'])

    @property
    def percent_done(self):
        return self.torrent[b'progress'] / 100
