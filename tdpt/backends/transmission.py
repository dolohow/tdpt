import base64

import transmission_rpc


class Client:
    """Handles connection to torrent client."""
    def __init__(self, config):
        """Creates new torrent client connection.

        Args:
            host (str): Hostname or IP address where client is litening.
            port (int): Port where client is listening.
        """
        self.transmission = transmission_rpc.Client(config['host'],
                                                    config['port'])

    def add_torrent(self, file_name, torrent, timeout=None, **kwargs):
        """Adds new torrent to download list.

        Args:
            torrent (telegram.File): File torrent object.
            timeout (int): Drop connection after timeout seconds.
        """
        barray = torrent.download_as_bytearray()
        filedump = base64.b64encode(barray).decode('utf-8')
        self.transmission.add_torrent(filedump, timeout, **kwargs)

    def get_torrents(self):
        """Yields Torrents objects."""
        yield from map(lambda torrent: Torrent(torrent),
                       self.transmission.get_torrents())


class Torrent:
    """Represents torrent in torrent client."""
    def __init__(self, torrent):
        """Creates new `Torrent` object"""
        self.torrent = torrent

    def is_downloading(self) -> bool:
        """bool: Is torrent currently downloading."""
        return self.torrent.status == 'downloading'

    def update(self):
        """Updates the torrent information."""
        self.torrent.update()

    @property
    def download_rate(self) -> int:
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
