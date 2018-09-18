"""
rest API tests
"""

import requests
import unittest
import json


class TestRest(unittest.TestCase):
    """unit test class for testing rest api"""

    def __init__(self, *args, **kwargs):
        super(TestRest, self).__init__(*args, **kwargs)
        # output everything
        self.full_print_mode = False

    def request(self, description, url, request_type, payload):
        url = 'http://35.166.169.63{}'.format(url)

        r = getattr(requests, request_type)(url,
                                            json=payload,
                                            headers={'Content-type': 'application/json'})

        curl = """
{}

curl -X {} \\
     -d \'{}\' \\
     {} \\
     --header "Content-Type:application/json"

return code: {}
return json:
{}
        """.format(description,
                   request_type.upper(),
                   json.dumps(payload), url, r.status_code, json.dumps(
                       json.loads(r.text), indent=4, separators=[',', ':']))

        # remove the trailing whitespace and print
        if self.full_print_mode:
            print "\n".join([line.strip() for line in curl.split("\n")])

        return r.status_code, json.loads(r.text)

    def setUp(self):
        for username in ['rexy', 'nootnoot']:
            description = "creating test accounts"
            payload = {'auth_token': 'admin_auth_token',
                       'user': 'admin',
                       'newuser': username}
            status, data = self.request(description, "/user", "post", payload)

        description = "create new playlist for user"
        payload = {'auth_token': 'nootnoot',
                   'user': 'nootnoot'}
        status, data = self.request(description, "/playlist", "post", payload)
        self.assertTrue(status == 200)
        self.nootnoot_playlist_id = data['data']

    def tearDown(self):
        description = "getting all users"
        payload = {'auth_token': "admin_auth_token",
                   'user': "admin"}
        status, data = self.request(description, "/user", "get", payload)

        existing_users = [user['name'] for user in data['data']['users']]

        delete = ['rexy', 'nootnoot']

        for user in existing_users:
            if user in delete or user.startswith("unittest_"):
                payload = {'auth_token': user,
                           'user':  user}
                status, data = self.request(
                    description, "/user", "delete", payload)

    def test_create_user_test_parameters(self):
        description = "testing missing parameter"

        payload = {'auth_token': 'admin_auth_token',
                   'user': 'admin'}
        status, data = self.request(description, "/user", "post", payload)
        self.assertTrue(status == 422)

    def test_create_user(self):
        description = "adding user named: unittest_rexy"

        payload = {'auth_token': 'admin_auth_token',
                   'user': 'admin',
                   'newuser': 'unittest_rexy'}
        status, data = self.request(description, "/user", "post", payload)
        self.assertTrue(status == 200)

    def test_create_user_as_unauthorized(self):
        description = "creating user while being unauthorized"

        payload = {'auth_token': 'rexy',
                   'user': 'rexy',
                   'newuser': 'unittest_rexy'}
        status, data = self.request(description, "/user", "post", payload)
        self.assertTrue(status == 401)

    def test_get_all_users(self):
        description = "get all users"

        payload = {'auth_token': "admin_auth_token",
                   'user': "admin"}
        status, data = self.request(description, "/user", "get", payload)
        self.assertTrue(status == 200)

    def test_get_all_users(self):
        description = "get all users while being unauthorized"

        payload = {'auth_token': "rexy",
                   'user': "rexy"}
        status, data = self.request(description, "/user", "get", payload)
        self.assertTrue(status == 401)

    def test_delete_user(self):
        description = "deleting user"
        payload = {'auth_token': 'rexy',
                   'user':  'rexy'}
        status, data = self.request(description, "/user", "delete", payload)
        self.assertTrue(status == 200)

        description = "get all users"
        payload = {'auth_token': "admin_auth_token",
                   'user': "admin"}
        status, data = self.request(description, "/user", "get", payload)
        self.assertTrue(status == 200)
        existing_users = [user['name'] for user in data['data']['users']]
        self.assertTrue('rexy' not in existing_users)

    def test_delete_user_unauthorized(self):
        description = "deleting user while unauthorized"
        payload = {'auth_token': 'nope',
                   'user':  'rexy'}
        status, data = self.request(description, "/user", "delete", payload)
        self.assertTrue(status == 401)

    def test_rename_user1(self):
        description = "renaming user"
        payload = {'auth_token': 'nootnoot',
                   'user': 'nootnoot',
                   'rename': 'unittest_nootnoot'}
        status, data = self.request(description, "/user", "put", payload)
        self.assertTrue(status == 200)

        description = "get all users"
        payload = {'auth_token': "admin_auth_token",
                   'user': "admin"}
        status, data = self.request(description, "/user", "get", payload)
        self.assertTrue(status == 200)
        existing_users = [user['name'] for user in data['data']['users']]
        self.assertTrue('nootnoot' not in existing_users)
        self.assertTrue('unittest_nootnoot' in existing_users)

    def test_rename_user_to_existing_username(self):
        description = "rename user to another existing username"
        payload = {'auth_token': 'nootnoot',
                   'user': 'nootnoot',
                   'rename': 'rexy'}
        status, data = self.request(description, "/user", "put", payload)
        self.assertTrue(status == 400)

    def test_playlist_new(self):

        description = "get playlists from rexy"
        payload = {'auth_token': 'rexy',
                   'user': 'rexy'}
        status, data = self.request(description, "/playlist", "get", payload)
        self.assertTrue(status == 200)
        playlist_count1 = len(data['data'])

        description = "create new playlist for user"
        payload = {'auth_token': 'rexy',
                   'user': 'rexy'}
        status, data = self.request(description, "/playlist", "post", payload)
        self.assertTrue(status == 200)

        description = "get playlists from rexy"
        payload = {'auth_token': 'rexy',
                   'user': 'rexy'}
        status, data = self.request(description, "/playlist", "get", payload)
        self.assertTrue(status == 200)
        playlist_count2 = len(data['data'])
        self.assertTrue(playlist_count2 - 1 == playlist_count1)

    def test_playlist_delete(self):

        description = "create new playlist for user"
        payload = {'auth_token': 'rexy',
                   'user': 'rexy'}
        status, data = self.request(description, "/playlist", "post", payload)
        self.assertTrue(status == 200)
        new_id = data['data']

        description = "get playlists from rexy"
        payload = {'auth_token': 'rexy',
                   'user': 'rexy'}
        status, data = self.request(description, "/playlist", "get", payload)
        self.assertTrue(status == 200)
        self.assertTrue(len(data['data']) == 1)

        description = "delete playlist"
        payload = {'auth_token': 'rexy',
                   'user': 'rexy',
                   'playlist': new_id}
        status, data = self.request(
            description, "/playlist", "delete", payload)
        self.assertTrue(status == 200)

        description = "get playlists from rexy"
        payload = {'auth_token': 'rexy',
                   'user': 'rexy'}
        status, data = self.request(description, "/playlist", "get", payload)
        self.assertTrue(status == 200)
        self.assertTrue(len(data['data']) == 0)

    def test_song_list(self):
        description = "get all songs"
        payload = {'auth_token': 'nootnoot',
                   'user': 'nootnoot'}
        status, data = self.request(description, "/song", "get", payload)
        self.assertTrue(len(data['data']) == 40)

    def test_song_add_to_playlist(self):

        description = "adding song to playlist"
        payload = {'auth_token': 'nootnoot',
                   'user': 'nootnoot',
                   'playlist': self.nootnoot_playlist_id,
                   'song': 1}
        status, data = self.request(
            description, "/playlist_songs", "post", payload)
        self.assertTrue(status == 200)

        description = "adding song to playlist"
        payload = {'auth_token': 'nootnoot',
                   'user': 'nootnoot',
                   'playlist': self.nootnoot_playlist_id,
                   'song': 2}
        status, data = self.request(
            description, "/playlist_songs", "post", payload)
        self.assertTrue(status == 200)

        description = "list songs in playlist"
        payload = {'auth_token': 'nootnoot',
                   'user': 'nootnoot',
                   'playlist': self.nootnoot_playlist_id
                   }
        status, data = self.request(
            description, "/playlist_songs", "get", payload)

        song_ids = [1, 2]
        for song in data['data']:
            self.assertTrue(song['id'] in song_ids)

    def test_song_delete(self):

        description = "adding song to playlist"
        payload = {'auth_token': 'nootnoot',
                   'user': 'nootnoot',
                   'playlist': self.nootnoot_playlist_id,
                   'song': 1}
        status, data = self.request(
            description, "/playlist_songs", "post", payload)
        self.assertTrue(status == 200)

        description = "list songs in playlist"
        payload = {'auth_token': 'nootnoot',
                   'user': 'nootnoot',
                   'playlist': self.nootnoot_playlist_id
                   }
        status, data = self.request(
            description, "/playlist_songs", "get", payload)
        self.assertTrue(len(data['data']) == 1)

        description = "delete song"
        payload = {'auth_token': 'rexy',
                   'user': 'rexy',
                   'playlist': self.nootnoot_playlist_id,
                   'song': 1}
        status, data = self.request(
            description, "/playlist_song", "delete", payload)

        description = "list songs in playlist"
        payload = {'auth_token': 'nootnoot',
                   'user': 'nootnoot',
                   'playlist': self.nootnoot_playlist_id
                   }
        status, data = self.request(
            description, "/playlist_songs", "get", payload)
        self.assertTrue(len(data['data']) == 1)

    def test_playlist_share_and_unshare(self):

        description = "share playlist"
        payload = {'auth_token': 'nootnoot',
                   'user': 'nootnoot',
                   'playlist': self.nootnoot_playlist_id,
                   'share_with': 'Albin Jaye'}
        status, data = self.request(description, "/share", "post", payload)
        self.assertTrue(status == 200)

        description = "list of users this playlist is shared with"
        payload = {'auth_token': 'nootnoot',
                   'user': 'nootnoot',
                   'playlist': self.nootnoot_playlist_id}
        status, data = self.request(description, "/share", "get", payload)
        self.assertTrue(data['data'][0] == "Albin Jaye")

    def test_bad_request(self):
        description = "testing bad url / bad request type"

        payload = {'auth_token': 'admin_auth_token',
                   'user': 'admin',
                   'newuser': 'unittest_rexy'}
        status, data = self.request(description, "/MONKEY", "post", payload)
        self.assertTrue(status == 404)

        description = "create new playlist for user"
        payload = {'auth_token': 'rexy',
                   'user': 'rexy'}
        status, data = self.request(description, "/playlist", "put", payload)
        self.assertTrue(status == 418)

    def test_full_dump(self):
        description = "get full data dump"

        payload = {'auth_token': 'rexy',
                   'user': 'rexy'}
        status, data = self.request(description, "/debug", "get", payload)

    def test_full_integration(self):

        for user in ['alice', 'george']:
            description = "adding user named: {}".format(user)
            payload = {'auth_token': 'admin_auth_token',
                       'user': 'admin',
                       'newuser': user}
            status, data = self.request(description, "/user", "post", payload)
            self.assertTrue(status == 200)

        description = "get list of all users - using the admin_auth_token"
        payload = {'auth_token': 'admin_auth_token',
                   'user': 'george'}
        status, data = self.request(description, "/user", "get", payload)
        self.assertTrue(status == 200)

        description = "george decides to change his name to carl"
        payload = {'auth_token': 'george',
                   'user': 'george',
                   'rename': 'carl'}
        status, data = self.request(description, "/user", "put", payload)
        self.assertTrue(status == 200)

        description = "create new playlist for carl and get the new playlist id"
        payload = {'auth_token': 'carl',
                   'user': 'carl'}
        status, data = self.request(description, "/playlist", "post", payload)
        playlist_id = data['data']
        self.assertTrue(status == 200)

        description = "carl wants to see his playlists"
        payload = {'auth_token': 'carl',
                   'user': 'carl'}
        status, data = self.request(description, "/playlist", "get", payload)

        description = "get full data dump for carl - should have empty playlist"
        payload = {'auth_token': 'carl',
                   'user': 'carl'}
        status, data = self.request(description, "/debug", "get", payload)

        description = "get full data dump for carl - should have empty playlist"
        payload = {'auth_token': 'carl',
                   'user': 'carl'}
        status, data = self.request(description, "/debug", "get", payload)

        description = "look at songs"
        payload = {'auth_token': 'carl',
                   'user': 'carl'}
        status, data = self.request(description, "/song", "get", payload)
        self.assertTrue(len(data['data']) == 40)

        description = "add song 13 to carl's playlist"

        payload = {'auth_token': 'carl',
                   'user': 'carl',
                   'playlist': playlist_id,
                   'song': 13}
        status, data = self.request(
            description, "/playlist_songs", "post", payload)
        self.assertTrue(status == 200)

        description = "add song 15 to carl's playlist"

        payload = {'auth_token': 'carl',
                   'user': 'carl',
                   'playlist': playlist_id,
                   'song': 15}
        status, data = self.request(
            description, "/playlist_songs", "post", payload)
        self.assertTrue(status == 200)

        description = "list songs in playlist {} should see 13 and 15".format(
            playlist_id)
        payload = {'auth_token': 'carl',
                   'user': 'carl',
                   'playlist': playlist_id
                   }
        status, data = self.request(
            description, "/playlist_songs", "get", payload)

        description = "share playlist {} with alice".format(playlist_id)
        payload = {'auth_token': 'carl',
                   'user': 'carl',
                   'playlist': playlist_id,
                   'share_with': 'alice'}
        status, data = self.request(description, "/share", "post", payload)
        self.assertTrue(status == 200)

        description = "get full data dump for carl - should be sharing playlist {}".format(
            playlist_id)
        payload = {'auth_token': 'carl',
                   'user': 'carl'}
        status, data = self.request(description, "/debug", "get", payload)

        description = "get full data dump for alice - should see id {} being shared".format(
            playlist_id)
        payload = {'auth_token': 'alice',
                   'user': 'alice'}
        status, data = self.request(description, "/debug", "get", payload)

        description = "carl deletes song 13 from playlist {}".format(
            playlist_id)
        payload = {'auth_token': 'carl',
                   'user': 'carl',
                   'playlist': playlist_id,
                   'song': 13}
        status, data = self.request(
            description, "/playlist_songs", "delete", payload)

        description = "alice can't see the song anymore".format(playlist_id)
        payload = {'auth_token': 'alice',
                   'user': 'alice',
                   'playlist': playlist_id
                   }
        status, data = self.request(
            description, "/playlist_songs", "get", payload)

        description = "carl sees all the users he is sharing playlist {} with".format(
            playlist_id)
        payload = {'auth_token': 'carl',
                   'user': 'carl',
                   'playlist': playlist_id}
        status, data = self.request(
            description, "/share", "get", payload)

        description = "carl unshares playlist {}".format(
            playlist_id)
        payload = {'auth_token': 'carl',
                   'user': 'carl',
                   'playlist': playlist_id,
                   'unshare_with': 'alice'}
        status, data = self.request(
            description, "/share", "delete", payload)

        description = "get full data dump for alice - should no shares".format(
            playlist_id)
        payload = {'auth_token': 'alice',
                   'user': 'alice'}
        status, data = self.request(description, "/debug", "get", payload)

        description = "carl deletes playlist {}".format(playlist_id)

        payload = {'auth_token': 'carl',
                   'user': 'carl',
                   'playlist': playlist_id}
        status, data = self.request(
            description, "/playlist", "delete", payload)
        self.assertTrue(status == 200)

        description = "get full data dump for carl - should have no playlist".format(
            playlist_id)
        payload = {'auth_token': 'carl',
                   'user': 'carl'}
        status, data = self.request(description, "/debug", "get", payload)

        for user in ['alice', 'carl']:
            description = "deleting user"
            payload = {'auth_token': user,
                       'user':  user}
            status, data = self.request(
                description, "/user", "delete", payload)
            self.assertTrue(status == 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
