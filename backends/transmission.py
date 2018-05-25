import transmissionrpc


class Client:
    """Handles connection to torrent client."""

    def __init__(self, host, port):
        """Creates new torrent client connection.

        Args:
            host (str): Hostname or IP address where client is litening.
            port (int): Port where client is listening.
        """
        self.transmission = transmissionrpc.Client(host, port)

    def get_torrents(self):
        """Yields Torrents objects."""
        yield from map(lambda torrent: Torrent(torrent),
                       self.transmission.get_torrents())


class Torrent:
    """Represents torrent in torrent client."""

    def __init__(self, torrent):
        """Creates new `Torrent` object"""
        self.torrent = torrent

    def update(self):
        """Updates the torrent information."""
        self.torrent.update()

    @property
    def download_rate(self):
        """int: Download rate in bps."""
        return self.torrent.rateDownload

    @property
    def eta(self):
        """datetime.timedelta: ETA for torrent completion."""
        try:
            return self.torrent.eta
        except ValueError:
            return 'Unavailable'

    @property
    def id(self):
        """str: Unique torrent identifier."""
        return self.torrent.id

    @property
    def name(self):
        """str: Torrent name."""
        return self.torrent.name

    @property
    def peers_connected(self):
        """int: Number of peers we are connected to."""
        return self.torrent.peersConnected

    @property
    def percent_done(self):
        """float: Download progress of selected files. 0.0 to 1.0."""
        return self.torrent.percentDone

    @property
    def status(self):
        """str: Torrent current status."""
        return self.torrent.status
