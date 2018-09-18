"""
provides database connection
base class for all the data access objects
"""
from excepts import DBException
import dataset


class Database(object):
    """
    provides database connection
    base class for all the database classes
    """

    def __init__(self):
        """
        constructor - sets up the database connection
        args: --
        """

        # tbd - move the database connection string to a
        # configuration file
        self.db = dataset.connect("sqlite:///db/playlist.sqlite")

        try:

            self.user = self.db['user']
            self.song = self.db['song']
            self.artist = self.db['artist']
            self.playlist = self.db['playlist']
            self.playlist_x_song = self.db['playlist_x_song']
            self.shared = self.db['shared']
        except Exception as error:
            raise DBException("database connection error")
