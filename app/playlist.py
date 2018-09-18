"""
the wsgi application that provides the rest services
"""
import json
import os
import sys
import urlparse

from werkzeug.exceptions import abort, HTTPException
from werkzeug.routing import Map, Rule
from werkzeug.utils import redirect
from werkzeug.wrappers import Request, Response
from werkzeug.wsgi import SharedDataMiddleware

# make sure we can reach the app libs
sys.path.insert(0, "lib")
from api import API
from excepts import APIException, APIAuthException, DBException


# special sauce
# use this decorator to wrap the rest endpoint methods
# will automatically check that user and auth_token
# are passed in with each request
# also intercepts and redispatches exceptions, translating
# exceptions into response numbers
def wrapper(fn):
    def wrapper_error(message, code):
        text = json.dumps({'error': message})
        response = Response(text, mimetype='application/json')
        response.status_code = code
        return response

    def inner(*args, **kwargs):
        try:
            self = args[0]
            request = args[1]
            data = json.loads(request.get_data())
            for key in ['user', 'auth_token']:
                if not key in data:
                    return wrapper_error("missing parameters", 401)
            api = API(name=data['user'], auth=data['auth_token'])
            return fn(self, request, api, **data)
        except APIException as e:
            return wrapper_error(str(e), 400)  # bad request
        except DBException as e:
            return wrapper_error(str(e), 503)  # service unavailable
        except APIAuthException as e:
            return wrapper_error(str(e), 401)  # unauthorized
        except Exception as e:
            # service unavailable
            print "server error:" + str(e)
            return wrapper_error("server error", 503)
    return inner


class RestServer(object):
    """playlist rest server"""

    def __init__(self):
        """
        constructor

        url -> method mapping goes here
        """
        # maps urls to methods
        self.url_map = Map([
            Rule('/debug', endpoint="debug"),
            Rule('/playlist', endpoint="playlist"),
            Rule('/playlist_songs', endpoint="playlist_songs"),
            Rule('/share', endpoint="share"),
            Rule('/song', endpoint="song"),
            Rule('/user', endpoint="user")])

    def wsgi_app(self, environ, start_response):
        """wsgi app"""

        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        """wsgi app method"""
        return self.wsgi_app(environ, start_response)

    def dispatch_request(self, request):
        """
        dispatch requests

        this is where the url endpoint mappings get rewritten
        to method names

        Ex:
            Rule('/playlist', endpoint="playlist"),

            the url /playlist gets rewritten to a call to the
            method self.rest_playlist here
        """
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'rest_' + endpoint)(request, **values)
        except HTTPException, e:
            return self.error_response('invalid url', 404)

    def error_response(self, message, code):
        """
        wrapper around an error response
        all error responses are in the json format of
           { 'status' : 'error',
             'data'   : <information about the error>}

        args:
           message - the information about the error
           code    - the response error code
        """
        text = json.dumps({'status': 'error',
                           'data': message})
        response = Response(text, mimetype='application/json')
        response.status_code = code
        return response

    def ok_response(self, message):
        """
        wrapper around a 200  response
        all ok responses are in the json format of
           { 'status' : 'ok',
             'data'   : <information>}

        args:
           message - the information to return
        """
        text = json.dumps({'status': 'ok',
                           'data': message})
        response = Response(text, mimetype='application/json')
        response.status_code = 200
        return response

    @wrapper
    def rest_debug(self, request, api, **data):

        # url    : /debug
        # method : GET
        # data   : ---
        # returns: full record for the current user
        if request.method == "GET":
            return self.ok_response(api.user_full_record())

        # post request placeholder for the future
        if request.method == "POST":
            return self.error_response('teapot', 418)

        # delete request placeholder for the future
        if request.method == "DELETE":
            return self.error_response('teapot', 418)

        # put request placeholder for the future
        if request.method == "PUT":
            return self.error_response('teapot', 418)

    @wrapper
    def rest_user(self, request, api, **data):

        # add a new user

        # url    : /user
        # method : POST
        # data   : newuser - the user to add

        if request.method == "POST":
            if not 'newuser' in data:
                return self.error_response("missing parameters", 422)
            api.user_add(data['newuser'])
            return self.ok_response("user added")

        # delete a user

        # url    : /user
        # method : DELETE
        # data   : --

        if request.method == "DELETE":
            api.user_delete()
            return self.ok_response("user deleted")

        # rename a user

        # url    : /user
        # method : PUT
        # data   : rename - the new name for the user

        if request.method == "PUT":
            if not 'rename' in data:
                return self.error_response("missing parameters", 422)
            api.user_rename(data['rename'])
            return self.ok_response("user renamed")

        # get all users

        # url    : /user
        # method : GET
        # data   : ---

        if request.method == "GET":
            users = api.users_all()
            return self.ok_response(users)

    @wrapper
    def rest_playlist(self, request, api, **data):

        # add an empty placelist to user

        # url    : /playlist
        # method : POST
        # data   : ---

        if request.method == "POST":
            playlist_id = api.playlist_add_empty()
            return self.ok_response(playlist_id)

        # delete a playlist from user

        # url    : /playlist
        # method : DELETE
        # data   : playlist - the playlist id to delete

        if request.method == "DELETE":
            if not 'playlist' in data:
                return self.error_response("missing parameters", 422)
            api.playlist_delete(data['playlist'])
            return self.ok_response("playlist deleted")

        # get all playlist ids for the user

        # url    : /playlist
        # method : GET
        # data   : ---
        # returns: list of playlist ids

        if request.method == "GET":
            ids = api.playlist_ids()
            return self.ok_response(ids)

        # put request placeholder for the future
        if request.method == "PUT":
            return self.error_response('teapot', 418)

    @wrapper
    def rest_playlist_songs(self, request, api, **data):

        # get all songs in a playlist

        # url    : /playlist_songs
        # method : GET
        # data   : playlist - playlist id
        # returns: list of dicts of songs and artists

        if request.method == "GET":
            if not 'playlist' in data:
                return self.error_response("missing parameters", 422)
            songs = api.playlist_songs_all(data['playlist'])
            return self.ok_response(songs)

        # puts song into playlist

        # url    : /playlist_songs
        # method : POST
        # data   : playlist - playlist id, song - song id to add

        if request.method == "POST":
            if not 'playlist' in data or not 'song' in data:
                return self.error_response("missing parameters", 422)

            api.playlist_add_song(data['playlist'], data['song'])
            return self.ok_response("song added to playlist")

        # delete a song from a playlist

        # url    : /playlist_songs
        # method : DELETE
        # data   : playlist - playlist id, song - song id to delete

        if request.method == "DELETE":
            if not 'playlist' in data or not 'song' in data:
                return self.error_response("missing parameters", 422)

            api.playlist_delete_song(data['playlist'], data['song'])
            return self.ok_response("song removed from playlist")

        # put request placeholder for the future
        if request.method == "PUT":
            return self.error_response('teapot', 418)

    @wrapper
    def rest_share(self, request, api, **data):

        # share a playlist with another user

        # url    : /share
        # method : POST
        # data   : playlist - playlist id, share_with - user to share with

        if request.method == "POST":
            if not 'playlist' in data or not 'share_with' in data:
                return self.error_response("missing parameters", 422)
            api.playlist_share(data['playlist'], data['share_with'])
            return self.ok_response("playlist shared")

        # unshare a playlist with another user

        # url    : /share
        # method : DELETE
        # data   : playlist - playlist id, unshare_with - user to unshare with

        if request.method == "DELETE":
            if not 'playlist' in data or not 'unshare_with' in data:
                return self.error_response("missing parameters", 422)
            api.playlist_unshare(data['playlist_id'], data['unshare_with'])
            return self.ok_response("playlist unshared")

        # get all users that you are sharing the playlist with

        # url    : /share
        # method : GET
        # data   : playlist - playlist id

        if request.method == "GET":
            if not 'playlist' in data:
                return self.error_response("missing parameters", 422)
            result = api.playlist_view_shared_to(data['playlist'])
            return self.ok_response(result)

        # put request placeholder for the future
        if request.method == "PUT":
            return self.error_response('teapot', 418)

    @wrapper
    def rest_song(self, request, api, **data):

        # get list of songs

        # url    : /share
        # method : GET
        # data   : ---
        # returns: list of dicts - song.id, title, artist

        if request.method == "GET":
            songs = api.song_list()
            return self.ok_response(songs)

        # put request placeholder for the future
        if request.method == "PUT":
            return self.error_response('teapot', 418)

        # post request placeholder for the future
        if request.method == "POST":
            return self.error_response('teapot', 418)

        # delete request placeholder for the future
        if request.method == "DELETE":
            return self.error_response('teapot', 418)


def create_app(with_static=True):
    """create the wsgi app"""
    app = RestServer()

    if with_static:
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static':  os.path.join(os.path.dirname(__file__), 'static')
        })
    return app


if __name__ == '__main__':
    # if we run playlist.py directly it will run in debug mode
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('172.30.0.243', 80, app, use_debugger=True, use_reloader=True)
