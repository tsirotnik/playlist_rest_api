## Overview

This is an example REST server for playlist sharing.  It will enable you to:

 - add/delete/rename users
 - create/delete playlists
 - share/unshare playlists with other users

## System/Environment
The playlist server is built on top of Apache using Python and WSGI.  The database engine is SQLite. To avoid conflicts with system applications the system Python and Apache are not used. Instead, we compile our own versions of Python and Apache and deploy to our application directory to compartmentalize the application and it's dependencies.

The install script located at **src/install.sh** will automatically download, compile and install Python, Apache, Pip and the required Python modules.  This has been tested on Ubuntu 18.04 LTS.  Your mileage may very depending on your system configuration.  Change the base path configuration in **src/install.sh** to install to the base directory where you have unpacked the server files.  The script does it's best to update your **.bashrc** automatically with the appropriate paths. Please check that it does so.

#### Example:
 - checkout files to /playlist
 - edit the BASE configuration variable in install.sh to "/playlist"
 - `cd src/; bash install.sh`
 - everything should automatically be installed

### Directories
This is a description of the directory structure and the files.

    ── app                       application directory
    |   ├── playlist.py          wsgi application
    |   ├── playlist.wsgi        wsgi loader
    │   ├── db                   database directory
    │   │   ├── dataloader.py    script to load rawdata into sqlite
    │   │   ├── import.sh        deletes existing database, runs dataloader
    │   │   ├── playlist.sqlite  sqlite db for playlist records
    │   │   ├── rawdata.txt      the original data file
    │   │   └── schema.sql       schema for sqlite db
    |   |
    │   ├── lib                  application libs
    │   │   ├── __init__.py
    │   │   ├── api.py           main application logic
    │   │   ├── database.py      database connector object
    │   │   └── excepts.py       custom exceptions
    |   |
    ├── src                      python/apache installed from here
    │   ├── install.sh           use this script to install app
    │   ├── sources              build from this directory
    │   └── tarballs             source files
    │   └── test
    │       ├── curl.py          client side tests for rest api
    │       ├── curl_output.txt  output from the curl test script
    │       ├── test.py          tests for the api
    │       └── test_output.txt  output of the api tests
    ├── bin                      python/apache will install here
    |
    └── start-server.sh

### Database

An sqlite database has been created for the playlist data. The schema is available in the file **db/schema.sql**. Note the delete triggers that should scavenge expired data on deletion of user or playlist.

The original json data is located in **db/rawdata.txt**.

To delete an existing database, create a new one and reload the data:
 - cd to the app directory
 - run `bash db/import.sh`

### Starting the server
 - cd to the app directory
 - run `bash start-server.sh`

This will start the apache server and run the wsgi playlist app.


### Starting the server in debug mode
- cd to the app directory
- run `python playlist.py`

This will start the apache server and run the wsgi playlist app in debug mode.

### Tests and Examples

There are 2 unit test scripts.

`curl.py` - makes requests against the rest server, it  can also be modified to output cli curl commands to be cut and paste into a terminal window.  You will find the output of this script in **app/tests/curl_output.txt**.  your can run this using:

    cd app
    python tests/curl.py

or just download it and runs on your own machine. Makes sure you have the python requests library installed:

    pip install requests


`test.py` - tests against the python api.  run this using

    cd app
    python tests/test.py

You will find the output of this script in
**app/tests/test_output.txt**

Examples of the REST API calls are in [REST_EXAMPLES.md](REST_EXAMPLES.md)



## Authorization
The rest server assumes that the user will get an authorization token from an authentication server prior to making the rest call. For now, the auth token is set to be the same as the username.

Any user can do administrative functions as long as the user uses the admin authorization token which is conveniently set to "admin_auth_token".

The rest api assumes that the actions taken are from the perspective of the user .

Examples:

User george wants to create a playlist. Since this is not an admin function, he will send a POST request using the regular authorization token to **/playlist** with:
username: george
auth_token: george

User george wants to create a new user. Since this is an admin function, he will send a POST request to **/user** using
username: george
auth_token: admin_auth_token

Please see the examples in the REST calls section of the document and in the file [REST_EXAMPLES.md](REST_EXAMPLES.md)

## Exceptions
Most exceptions are caught and translated into response codes in **app/playlist.py**.  See the decorator function **wrapper** in **app/playlist.py** for more details.  Unit tests cover most of the exceptions and should be low effort to add more checking or change the response codes as needed.

## REST calls

> If you are cutting and pasting the below curl examples beware of
> trailing whitepace on the multiline bash commands.

> see [REST_EXAMPLES.md](REST_EXAMPLES.md) for more examples



**add user**

- URL : /user
- Method : POST
- URL Params : auth_token, newuser, user

*Ex: user: admin creates a new user named alice, admin must authenticate with the admin token*

    curl -X POST \
    -d '{"auth_token": "admin_auth_token", "newuser": "alice", "user": "admin"}' \
    http://35.166.169.63/user \
    --header "Content-Type:application/json"

    return code: 200
    return json:
    {
    "status":"ok",
    "data":"user added"
    }



**delete user**

- URL : /user
- Method : DELETE
- URL Params : auth_token, user

*Ex: alice deletes her user account*

    curl -X DELETE \
    -d '{"auth_token": "alice", "user": "alice"}' \
    http://35.166.169.63/user \
    --header "Content-Type:application/json"

    return code: 200
    return json:
    {
    "status":"ok",
    "data":"user deleted"
    }

**rename user**

- URL : /user
- Method : PUT
- URL Params : auth_token, user,rename

*ex: george changes his name to carl*

    curl -X PUT \
    -d '{"rename": "carl", "auth_token": "george", "user": "george"}' \
    http://35.166.169.63/user \
    --header "Content-Type:application/json"

    return code: 200
    return json:
    {
    "status":"ok",
    "data":"user renamed"
    }

**list all users**

- URL : /user
- Method : GET
- URL Params : auth_token, user

*Ex: user: george gets the list of users, george must authenticate with the admin token because only admins can get the list of users*

    curl -X GET \
    -d '{"auth_token": "admin_auth_token", "user": "george"}' \
    http://35.166.169.63/user \
    --header "Content-Type:application/json"

    return code: 200
    return json:
    {
    "status":"ok",
    "data":{
    "users":[
    {
    "id":1,
    "name":"Albin Jaye"
    }, ...

**list all songs**

- URL : /song
- Method : GET
- URL Params : auth_token, user

*Ex: user carl wants a list of all the songs*

    curl -X GET \
    -d '{"auth_token": "carl", "user": "carl"}' \
    http://35.166.169.63/song \
    --header "Content-Type:application/json"

    return code: 200
    return json:
    {
    "status":"ok",
    "data":[
    {
    "artist":"Camila Cabello",
    "id":1,
    "title":"Never Be the Same"
    },...

**create a playlist**

- URL : /playlist
- Method : POST
- URL Params : auth_token, user

*Ex: create new empty playlist for carl and return the playlist id*

    curl -X POST \
    -d '{"auth_token": "carl", "user": "carl"}' \
    http://35.166.169.63/playlist \
    --header "Content-Type:application/json"

    return code: 200
    return json:
    {
    "status":"ok",
    "data":6
    }

**delete playlist**

- URL : /playlist
- Method : DELETE
- URL Params : auth_token, user, playlist

*Ex: carl deletes playlist_id 6*

    curl -X DELETE \
    -d '{"auth_token": "carl", "playlist": 6, "user": "carl"}' \
    http://35.166.169.63/playlist \
    --header "Content-Type:application/json"

    return code: 200
    return json:
    {
    "status":"ok",
    "data":"playlist deleted"
    }

**add song to playlist**

- URL : /playlist_songs
- Method : POST
- URL Params : auth_token, user, playlist, song

*Ex: carl adds song_id 15 to his playlist with id 6*

    curl -X POST \
    -d '{"auth_token": "carl", "playlist": 6, "user": "carl", "song": 15}' \
    http://35.166.169.63/playlist_songs \
    --header "Content-Type:application/json"

    return code: 200
    return json:
    {
    "status":"ok",
    "data":"song added to playlist"
    }

   **delete song from playlist**

- URL : /playlist_songs
- Method : DELETE
- URL Params : auth_token, user, playlist, song

*Carl deletes song 13 from playlist 6*

    curl -X DELETE \
    -d '{"auth_token": "carl", "playlist": 6, "user": "carl", "song": 13}' \
    http://35.166.169.63/playlist_songs \
    --header "Content-Type:application/json"

    return code: 200
    return json:
    {
    "status":"ok",
    "data":"song removed from playlist"
    }

** list songs in playlist **

- URL : /playlist_songs
- Method : GET
- URL Params : auth_token, user, playlist

*Ex: alice wants a list of songs from playlist id 6*

    curl -X GET \
    -d '{"auth_token": "alice", "playlist": 6, "user": "alice"}' \
    http://35.166.169.63/playlist_songs \
    --header "Content-Type:application/json"

    return code: 200
    return json:
    {
    "status":"ok",
    "data":[
    {
    "artist":"Kendrick Lamar",
    "id":15,
    "title":"All The Stars"
    }
    ]
    }

 **share playlist**

- URL : /share
- Method : POST
- URL Params : auth_token, user, playlist, share_with

*Ex: carl wants to share playlist id 6 with alice*

    curl -X POST \
    -d '{"auth_token": "carl", "playlist": 6, "user": "carl", "share_with": "alice"}' \
    http://35.166.169.63/share \
    --header "Content-Type:application/json"

    return code: 200
    return json:
    {
    "status":"ok",
    "data":"playlist shared"
    }

**unshare playlist**

- URL : /share
- Method : DELETE
- URL Params : auth_token, user, playlist, unshare_with

*Ex: carl hates alice, he wants to unshare playlist id 6*

    curl -X DELETE \
    -d '{"unshare_with": "alice", "auth_token": "carl", "playlist": 6, "user": "carl"}' \
    http://35.166.169.63/share \
    --header "Content-Type:application/json"

    return code: 503
    return json:
    {
    "error":"server error"
    }

**list of users playlist is shared with**

- URL : /share
- Method : DELETE
- URL Params : auth_token, user, playlist, unshare_with

*Ex: carl wants to see all the users he's shared playlist id 6 with*

    curl -X GET \
    -d '{"auth_token": "carl", "playlist": 6, "user": "carl"}' \
    http://35.166.169.63/share \
    --header "Content-Type:application/json"

    return code: 200
    return json:
    {
    "status":"ok",
    "data":[
    "alice"
    ]
    }


**full debug dump for user**

- URL : /debug
- Method : GET
- URL Params : auth_token, user

 *Ex: get all the information about user alice*

    curl -X GET \
    -d '{"auth_token": "alice", "user": "alice"}' \
    http://35.166.169.63/debug \
    --header "Content-Type:application/json"

    return code: 200
    return json:
    {
    "status":"ok",
    "data":{
    "playlist_shared_with_user":[],
    "playlists":[],
    "playlist_shared_with_this_user":[
    {
    "playlist_id":6,
    "songs":[
    {
    "artist":"Ariana Grande",
    "id":13,
    "title":"No Tears Left To Cry"
    },
    {
    "artist":"Kendrick Lamar",
    "id":15,
    "title":"All The Stars"
    }
    ]
    }
    ],
    "user":{
    "name":"alice",
    "id":13
    }
    }
    }
