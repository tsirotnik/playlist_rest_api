"""
utility script imports raw data into sqlite database
"""

import json
import os
import sys

sys.path.append("lib")
from database import Database


class Loader(object):
    """
    Loader object that imports json data into sqlite
    """

    def __init__(self):
        """
        constructor
        """
        # relative path to the json formatted file to load
        # uses the database object
        # for name and path to database see database object
        self.rawdata_path = "db/rawdata.txt"
        self.db = Database()

    def load(self):
        """
        imports the data into database
        """

        # read json data from file
        try:
            with open(self.rawdata_path) as fh:
                data = json.loads(fh.read())
        except Exception as e:
            print "\nunable to load data from rawdata file {}\n".format(
                self.rawdata_path)
            raise e

        users = data['users']
        playlists = data['playlists']
        songs = data['songs']

        # insert user data
        try:
            for user in users:
                self.db.user.insert(user)
        except Exception as e:
            print "\nunable to load data into table:user\n"
            raise e

        # insert song data
        try:
            for song in songs:
                artist = self.db.artist.find_one(artist=song['artist'])
                if artist:
                    artist_id = artist['id']
                else:
                    artist_id = self.db.artist.insert(
                        {'artist': song['artist']})

                converted_data = {'artist_id': artist_id,
                                  'title': song['title']}

                self.db.song.insert(converted_data)
        except Exception as e:
            print "\nunable to load data into table:song\n"
            raise e

        # insert playlist data
        try:
            for playlist in playlists:
                converted_data = {'id': playlist['id'],
                                  'user_id': playlist['owner_id']}
                self.db.playlist.insert(converted_data)

                for song_id in playlist['song_ids']:
                    converted_data = {'id': None,
                                      'playlist_id': playlist['id'],
                                      'song_id': song_id}
                    self.db.playlist_x_song.insert(converted_data)
        except Exception as e:
            print "\nunable to load data into table:playlist\n"
            raise e


if __name__ == "__main__":
    Loader().load()
