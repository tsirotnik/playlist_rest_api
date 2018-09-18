"""
main API for the playlist backend
"""

from database import Database
from excepts import APIException, APIAuthException
from functools import wraps
import json
import os
import sys


class API(object):
    """
    Main dispatch object for all the backend calls
    """

    def __init__(self, name=None, auth=None):
        """
        Constructor

        Args:
           name - username that you will be performing tasks as
           auth - auth token, currently either:
                    - the same as the username for regular users
                    or
                    - "admin_auth_token" which lets the user perform admin
                       tasks.  currently the only admin task is creating a
                       new user
        """

        # razor thin mock up authentication
        # basically you either provide an auth_token which is conveniently the
        # same as your username or you provide the auth token "admin_auth_token"

        if not auth:
            raise APIAuthException("auth token needed")

        if not name:
            raise APIAuthException("username needed")

        if auth == "admin_auth_token":
            self.admin_ok = True
        else:
            self.admin_ok = False
            if auth != name:
                raise APIAuthException("auth token invalid")

        # get the database connections
        # if you are looking to change the name or path to
        # the database, look in the Database module
        self.db = Database()

        # set the name and ensure that the name is valid
        self.name = name
        self.assert_user_exists(self.name)

    # -----------------------------------------------------------
    # assertions
    #
    # these assertions will check basic requirements
    # and throw an exception if they are not met
    #
    # method calls use these assertions first before processing
    # begins to ensure that all basic requirements have been met
    # -----------------------------------------------------------

    def assert_admin_ok(self):
        """throw an exception if the admin token was not provided"""
        if not self.admin_ok:
            raise APIAuthException("needs admin priviledges")

    def assert_song_exists(self, song_id):
        """throws an exception if the song_id does not exist"""
        if not self.song_exists(song_id):
            raise APIException("song does not exist")

    def assert_song_not_exists(self, song_id):
        """throws an exception if the song_id exists"""
        if self.song_exists(song_id):
            raise APIException("pre-existing song error")

    def assert_song_in_playlist(self, playlist_id, song):
        """throw exception if song not in playlist"""
        self.assert_user_owns_playlist(playlist_id)
        if not self.song_in_playlist(playlist_id, song):
            raise APIException("song not in playlist")

    def assert_song_not_in_playlist(self, playlist_id, song):
        """throw exception if song in playlist"""
        self.assert_user_owns_playlist(playlist_id)
        if self.song_in_playlist(playlist_id, song):
            raise APIException("song already in playlist")

    def assert_playlist_exists(self, playlist_id):
        """throws an exception if the playlist exists"""
        if not self.db.playlist.find_one(id=playlist_id):
            raise APIException(
                "playlist id {} does not exist".format(playlist_id))

    def assert_user_exists(self, name):
        """throw an exception if the user does not exist"""

        if not self.user_id(name):
            raise APIException("user does not exist")

    def assert_user_not_exists(self, name):
        """throws an exception if the user exists"""

        if self.user_id(name):
            raise APIException("prexisting user")

    def assert_user_owns_playlist(self, playlist_id):
        """
        throws an exception if the playlist is not owned by the current
        "logged in" i.e. the user is self.name
        """

        self.assert_playlist_exists(playlist_id)
        if not playlist_id in self.playlist_ids():
            raise APIException("playlist not valid for user")

    def assert_playlist_viewable(self, playlist_id):
        """
        throws an exception if the playlist is not owned by the current
        "logged in" i.e. the user is self.name and if the playlist
        is not shared
        """
        self.assert_playlist_exists(playlist_id)

        record = self.db.shared.find_one(
            playlist_id=playlist_id, shared_to_user_id=self.user_id(self.name))

        if not record and not playlist_id in self.playlist_ids():
            raise APIException("playlist not valid for user")

    # -----------------------------------------------------------
    # user methods
    # -----------------------------------------------------------

    def user_add(self, name):
        """
        add a user

        args:
           username

        this can be done by any user, but that user must have provided a
        admin_auth_token
        """
        self.assert_admin_ok()
        self.assert_user_not_exists(name)
        self.db.user.insert({'name': name})

    def user_delete(self):
        """delete a user by name"""
        self.db.user.delete(name=self.name)

    def user_exists(self, name):
        """True or False if the user exists or not"""

        return True if self.user_id(name) else False

    def user_id(self, name):
        """get the user.id from the database for the user name"""

        user = self.db.user.find_one(name=name)
        return user['id'] if user else None

    def user_rename(self, rename):
        """rename the current user to a new name"""
        self.assert_user_not_exists(rename)
        self.db.user.update(
            {'name': rename, 'id': self.user_id(self.name)}, ['id'])
        self.name = rename

    def users_all(self):
        """return all users"""
        self.assert_admin_ok()
        rows = self.db.user.find(order_by=['id'])
        return {'users': [dict(row) for row in rows]}

    # -----------------------------------------------------------
    # song methods
    # -----------------------------------------------------------

    def song_exists(self, song_id):
        """True or False if song in the database"""

        song = self.db.song.find_one(id=song_id)
        return True if song else False

    def song_list(self):
        """Get all songs"""

        statement = """
                      select song.id, song.title, artist.artist
                      from song, artist
                      where song.artist_id = artist.id
                      order by song.id
        """
        songs = self.db.db.query(statement)
        songs = [dict(song) for song in songs]
        return songs

    # -----------------------------------------------------------
    # playlist methods
    # -----------------------------------------------------------

    def playlist_ids(self):
        """return list of playlist ids for the user"""
        return [playlist['id'] for playlist in self.db.playlist.find(
            user_id=self.user_id(self.name))]

    def song_in_playlist(self, playlist_id, song_id):
        """True or False - song is in playlist"""
        self.assert_song_exists(song_id)
        self.assert_playlist_exists(playlist_id)
        self.assert_user_owns_playlist(playlist_id)
        result = self.db.playlist_x_song.find_one(
            song_id=song_id, playlist_id=playlist_id)
        return True if result else False

    def playlist_add_empty(self):
        """give the current user a new empty playlist"""
        return self.db.playlist.insert({'user_id': self.user_id(self.name)})

    def playlist_delete(self, playlist_id):
        """delete a playlist"""
        self.assert_user_owns_playlist(playlist_id)
        self.db.playlist.delete(id=playlist_id)

    def playlist_add_song(self, playlist_id, song_id):
        """add a song to a playlist"""
        self.assert_song_exists(song_id)
        self.assert_user_owns_playlist(playlist_id)
        self.assert_song_not_in_playlist(playlist_id, song_id)
        self.db.playlist_x_song.insert(
            {'playlist_id': playlist_id, 'song_id': song_id})

    def playlist_delete_song(self, playlist_id, song_id):
        """ delete a song from a playlist"""
        self.assert_song_exists(song_id)
        self.assert_user_owns_playlist(playlist_id)
        self.assert_song_in_playlist(playlist_id, song_id)
        self.db.playlist_x_song.delete(
            **{'playlist_id': playlist_id, 'song_id': song_id})

    def playlist_share(self, playlist_id, share_with):
        """share a playlist with another user(by name)"""
        self.assert_user_exists(share_with)
        self.assert_user_owns_playlist(playlist_id)

        user_id = self.user_id(self.name)
        shared_with_id = self.user_id(share_with)

        if user_id == shared_with_id:
            raise APIException("cannot share a playlist with yourself")

        self.db.shared.upsert({'playlist_id': playlist_id,
                               "shared_to_user_id": shared_with_id}, ['playlist_id', 'shared_to_user_id'])

    def playlist_unshare(self, playlist_id, unshare_with):
        """ stop sharing a playlist with another user(by name)"""
        self.assert_user_owns_playlist(self.name, playlist_id)
        self.assert_user_exists(unshare_with)

        user_id = self.user_id(self.name)
        unshare_with_id = self.user_id(unshare_with)

        self.db.shared.delete(playlist_id=playlist_id,
                              shared_to_user_id=unshare_with_id)

    def playlist_songs_all(self, playlist_id):
        """"return a list of song titles and artists for a playlist"""
        self.assert_playlist_viewable(playlist_id)
        statement = """
                      select song.id, song.title, artist.artist
                      from song, artist, playlist_x_song
                      where playlist_x_song.song_id = song.id
                      and song.artist_id = artist.id
                      and playlist_x_song.playlist_id = {}
                      order by playlist_x_song.id
        """.format(playlist_id)

        return [dict(row) for row in self.db.db.query(statement)]

    def playlist_view_shared_to(self, playlist_id):
        """return all the users the playlist is shared to"""
        self.assert_playlist_exists(playlist_id)
        self.assert_user_owns_playlist(playlist_id)

        shared = self.db.shared.find(playlist_id=playlist_id)

        shared_to = []

        for share in shared:
            user = self.db.user.find_one(id=share['shared_to_user_id'])
            shared_to.append(user['name'])
        return shared_to

    def user_full_record(self):
        """data dump of full user record"""
        user = self.db.user.find_one(name=self.name, order_by=['id'])
        record = {'user': {'name': user['name'],
                           'id': user['id']},
                  'playlists': [],
                  'playlist_shared_with_user': []}

        # is there a way to do this more inelegantly, showing a
        # greater lack of artistry?  no, there is not
        #
        # playlists owned by user
        playlists = self.db.playlist.find(user_id=user['id'])

        for playlist in playlists:
            playlist_record = {'playlist_id': playlist['id']}
            playlist_record['songs'] = self.playlist_songs_all(playlist['id'])

            shared = self.db.shared.find(playlist_id=playlist['id'])
            for share in shared:
                users = self.db.user.find(id=share['shared_to_user_id'])
                for user in users:
                    if not 'shared_to' in playlist_record:
                        playlist_record['shared_to'] = []
                    playlist_record['shared_to'].append(user['name'])

            record['playlists'].append(playlist_record)

        shared = self.db.shared.find(
            shared_to_user_id=self.user_id(self.name))

        shared_with = []
        for share in shared:
            playlist_id = share['playlist_id']
            data = {'playlist_id': playlist_id,
                    'songs': self.playlist_songs_all(playlist_id)}
            shared_with.append(data)
        if shared_with:
            record['playlist_shared_with_this_user'] = shared_with

        return record
        return json.dumps(record, indent=4, separators=[',', ':'])


if __name__ == "__main__":
    api = API("Albin Jaye", "Albin Jaye")
    id = api.playlist_add_empty()
    api.playlist_add_song(id, 31)
    api.playlist_share(id, 'Dipika Crescentia')
    api.user_full_record()

    print api.user_full_record()
    print
    print

    api = API("Dipika Crescentia", "Dipika Crescentia")
    print api.user_full_record()
