import datetime
import math
import xmlrpc.client


class Client:

    def __init__(self, config):
        url = f'http://{config["host"]}:{config["port"]}/RPC2'
        self.config = config
        self.proxy = xmlrpc.client.ServerProxy(url, verbose=False)

    def add_torrent(self, file_name, torrent, timeout=None, **kwargs):
        self.proxy.load.start_verbose(
            '',
            torrent.file_path,
            [f'd.custom1.set={self.config["set_label"]}'])

    def get_torrents(self):
        yield from map(lambda torrent: Torrent(torrent, self.proxy),
                       self.proxy.download_list())


class Torrent:

    PROPERTIES = {
        'chunk_size': 0,
        'completed_bytes': 1,
        'completed_chunks': 2,
        'down.rate': 3,
        'incomplete': 4,
        'is_active': 5,
        'is_open': 6,
        'name': 7,
        'peers_connected': 8,
        'size_bytes': 9,
        'size_chunks': 10,
    }

    def __init__(self, torrent, proxy):
        self.torrent = torrent
        self.proxy = proxy

        self.multicall = xmlrpc.client.MultiCall(self.proxy)
        for prop in self.PROPERTIES:
            getattr(self.multicall, 'd.' + prop)(self.torrent)
        self.update()

    def is_downloading(self):
        return (self.__get_prop('down.rate') and
                self.__get_prop('is_open') and
                self.__get_prop('is_active'))

    def update(self):
        try:
            self.data = tuple(self.multicall())
        except:
            raise KeyError

    @property
    def download_rate(self):
        return self.__get_prop('down.rate')

    @property
    def eta(self):
        if self.__get_prop('down.rate') == 0:
            return 'Unavailable'
        chunks_left = (self.__get_prop('size_chunks') -
                       self.__get_prop('completed_chunks'))
        down_rate = (chunks_left *
                     self.__get_prop('chunk_size') /
                     self.__get_prop('down.rate'))
        return datetime.timedelta(seconds=math.floor(down_rate))

    @property
    def id(self):
        return self.torrent

    @property
    def name(self):
        return self.__get_prop('name')

    @property
    def peers_connected(self):
        return self.__get_prop('peers_connected')

    @property
    def percent_done(self):
        return (self.__get_prop('completed_bytes') /
                               self.__get_prop('size_bytes'))

    def __get_prop(self, prop):
        return self.data[self.PROPERTIES[prop]]
