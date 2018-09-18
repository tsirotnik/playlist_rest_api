import sys

sys.path.append("lib")


import unittest
from api import API
from excepts import APIException

class Tests(unittest.TestCase):
    def setUp(self):
        api = API("admin", "admin_auth_token")

        api.db.user.delete(name="rexy")
        api.db.user.delete(name="nootnoot")

        self.rexy_id = api.user_add("rexy")
        self.nootnoot_id = api.user_add("nootnoot")

    def tearDown(self):
        api = API("admin", "admin_auth_token")
        api.db.user.delete(name="rexy")
        api.db.user.delete(name="nootnoot")

    def user_add(self):
        api = API("rexy", "rexy")
        with self.assertRaises(APIAuthException) as context:
            api.user_add("newuser")
        self.assertTrue(context.exception)

        api = API("admin", "rexy")
        with self.assertRaises(APIAuthException) as context:
            api.user_add("newuser")
        self.assertTrue(context.exception)

        api = API("rexy", "admin_auth_token")
        api.user_add("newuser")

        api = API("admin", "admin_auth_token")
        api.user_add("newuser2")

        api.db.user.delete(name="newuser")
        api.db.user.delete(name="newuser2")

    def test_user_id(self):
        api = API("admin", "admin_auth_token")
        user_id = api.user_id("Albin Jaye")
        self.assertTrue(user_id == 1)

    def test_assert_user_exists(self):
        api = API("admin", "admin_auth_token")
        api.assert_user_exists("Albin Jaye")

        with self.assertRaises(APIException) as context:
            api.assert_user_exists("not Albin Jaye")
        self.assertTrue(context.exception)

    def test_assert_user_not_exists(self):
        api = API("admin", "admin_auth_token")
        api.assert_user_not_exists("bad name")

        with self.assertRaises(APIException) as context:
            api.assert_user_not_exists("Albin Jaye")
        self.assertTrue(context.exception)

    def test_user_delete(self):
        api = API("rexy", "rexy")
        api.user_delete()

        api2 = API("admin", "admin_auth_token")
        api2.assert_user_not_exists("rexy")

    def test_user_rename(self):
        api = API("rexy", "rexy")
        api.assert_user_not_exists("new fancy rexy")
        api.user_rename("new fancy rexy")

        api.assert_user_not_exists("rexy")
        api.assert_user_exists("new fancy rexy")

        api.user_delete()

    # --------------------------------------------------------------------

    def test_song_exists(self):
        api = API("admin", "admin_auth_token")
        self.assertTrue(api.song_exists(31))
        self.assertFalse(api.song_exists(9999))

    def test_assert_song_exists(self):
        api = API("admin", "admin_auth_token")
        with self.assertRaises(APIException) as context:
            api.assert_song_exists(9999)
        self.assertTrue(context.exception)

        api.assert_song_exists(31)

    def test_assert_song_not_exists(self):
        api = API("admin", "admin_auth_token")
        with self.assertRaises(APIException) as context:
            api.assert_song_not_exists(31)
        self.assertTrue(context.exception)

        api.assert_song_not_exists(9999)

    # --------------------------------------------------------------------
    def playlist_ids(self):
        api = API("Dipika Crescentia", "Dipika Crescentia")
        self.assertTrue(api.playlist_ids()[0] == 1)

    def test_assert_user_owns_playlist(self):
        api = API("Dipika Crescentia", "Dipika Crescentia")
        api.assert_user_owns_playlist(1)

        # playlist not valid
        with self.assertRaises(APIException) as context:
            api.assert_user_owns_playlist(2)
        self.assertTrue(context.exception)

    # --------------------------------------------------------------------

    def test_song_in_playlist(self):
        api = API("Dipika Crescentia", "Dipika Crescentia")
        self.assertTrue(api.song_in_playlist(1, 8))
        self.assertFalse(api.song_in_playlist(1, 31))

        # doest own playlist
        with self.assertRaises(APIException) as context:
            api.song_in_playlist(2, 10)
        self.assertTrue(context.exception)

    def test_assert_song_in_playlist(self):
        api = API("Dipika Crescentia", "Dipika Crescentia")
        api.assert_song_in_playlist(1, 8)

        with self.assertRaises(APIException) as context:
            api.assert_song_in_playlist(1, 10)
        self.assertTrue(context.exception)

        # doest own playlist
        with self.assertRaises(APIException) as context:
            api.assert_song_in_playlist(2, 10)
        self.assertTrue(context.exception)

    def test_assert_song_not_in_playlist(self):
        api = API("Dipika Crescentia", "Dipika Crescentia")
        api.assert_song_not_in_playlist(1, 31)

        with self.assertRaises(APIException) as context:
            api.assert_song_not_in_playlist(1, 8)
        self.assertTrue(context.exception)

        # doest own playlist
        with self.assertRaises(APIException) as context:
            api.assert_song_not_in_playlist(2, 8)
        self.assertTrue(context.exception)

    # --------------------------------------------------------------------

    def test_playlist_add(self):

        api = API("rexy", "rexy")

        playlists = api.playlist_ids()
        api.playlist_add_empty()

        playlists2 = api.playlist_ids()

        self.assertTrue(len(playlists)+1 == len(playlists2))

    def test_playlist_add_song(self):

        api = API("rexy", "rexy")

        playlist_id = api.playlist_add_empty()

        api.playlist_add_song(playlist_id, 31)
        api.assert_song_in_playlist(playlist_id, 31)

    def test_playlist_delete_song(self):

        api = API("rexy", "rexy")
        playlist_id = api.playlist_add_empty()

        api.playlist_add_song(playlist_id, 31)
        api.assert_song_in_playlist(playlist_id, 31)
        api.playlist_delete_song(playlist_id, 31)
        api.assert_song_not_in_playlist(playlist_id, 31)


if __name__ == "__main__":
    unittest.main(verbosity=2)
