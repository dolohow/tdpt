import transmissionrpc


class Client:

    def __init__(self, host, port):
        self.transmission = transmissionrpc.Client(host, port)

    def get_torrents(self):
        yield from map(lambda torrent: Torrent(torrent),
                       self.transmission.get_torrents())


class Torrent:

    def __init__(self, torrent):
        self.torrent = torrent

    def update(self):
        self.torrent.update()

    @property
    def download_rate(self):
        return self.torrent.rateDownload

    @property
    def eta(self):
        try:
            return self.torrent.eta
        except ValueError:
            return 'Unavailable'

    @property
    def id(self):
        return self.torrent.id

    @property
    def name(self):
        return self.torrent.name

    @property
    def peers_connected(self):
        return self.torrent.peersConnected

    @property
    def percent_done(self):
        return self.torrent.percentDone

    @property
    def status(self):
        return self.torrent.status
