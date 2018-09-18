> If you are cutting and pasting the below curl examples beware of
> trailing whitepace on the multiline bash commands.

**adding user named: alice**

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


**adding user named: george**

    curl -X POST \
    -d '{"auth_token": "admin_auth_token", "newuser": "george", "user": "admin"}' \
    http://35.166.169.63/user \
    --header "Content-Type:application/json"
    
    return code: 200
    return json:
    {
    "status":"ok",
    "data":"user added"
    }


**get list of all users - using the admin_auth_token**

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
    },
    {
    "id":2,
    "name":"Dipika Crescentia"
    },
    {
    "id":3,
    "name":"Ankit Sacnite"
    },
    {
    "id":4,
    "name":"Galenos Neville"
    },
    {
    "id":5,
    "name":"Loviise Nagib"
    },
    {
    "id":6,
    "name":"Ryo Daiki"
    },
    {
    "id":7,
    "name":"Seyyit Nedim"
    },
    {
    "id":8,
    "name":"admin"
    },
    {
    "id":17,
    "name":"alice"
    },
    {
    "id":18,
    "name":"george"
    }
    ]
    }
    }


**george decides to change his name to carl**

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


**create new playlist for carl and get the new playlist id**

    curl -X POST \
    -d '{"auth_token": "carl", "user": "carl"}' \
    http://35.166.169.63/playlist \
    --header "Content-Type:application/json"
    
    return code: 200
    return json:
    {
    "status":"ok",
    "data":8
    }


**carl wants to see his playlists**

    curl -X GET \
    -d '{"auth_token": "carl", "user": "carl"}' \
    http://35.166.169.63/playlist \
    --header "Content-Type:application/json"
    
    return code: 200
    return json:
    {
    "status":"ok",
    "data":[
    8
    ]
    }


**get full data dump for carl - should have empty playlist**

    curl -X GET \
    -d '{"auth_token": "carl", "user": "carl"}' \
    http://35.166.169.63/debug \
    --header "Content-Type:application/json"
    
    return code: 200
    return json:
    {
    "status":"ok",
    "data":{
    "playlist_shared_with_user":[],
    "playlists":[
    {
    "playlist_id":8,
    "songs":[]
    }
    ],
    "user":{
    "name":"carl",
    "id":18
    }
    }
    }


**get full data dump for carl - should have empty playlist**

    curl -X GET \
    -d '{"auth_token": "carl", "user": "carl"}' \
    http://35.166.169.63/debug \
    --header "Content-Type:application/json"
    
    return code: 200
    return json:
    {
    "status":"ok",
    "data":{
    "playlist_shared_with_user":[],
    "playlists":[
    {
    "playlist_id":8,
    "songs":[]
    }
    ],
    "user":{
    "name":"carl",
    "id":18
    }
    }
    }


****look at songs****

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
    },
    {
    "artist":"Zedd",
    "id":2,
    "title":"The Middle"
    },
    {
    "artist":"The Weeknd",
    "id":3,
    "title":"Pray For Me"
    },
    {
    "artist":"Drake",
    "id":4,
    "title":"God's Plan"
    },
    {
    "artist":"Bebe Rexha",
    "id":5,
    "title":"Meant to Be"
    },
    {
    "artist":"Imagine Dragons",
    "id":6,
    "title":"Whatever It Takes"
    },
    {
    "artist":"Maroon 5",
    "id":7,
    "title":"Wait"
    },
    {
    "artist":"Bazzi",
    "id":8,
    "title":"Mine"
    },
    {
    "artist":"Marshmello",
    "id":9,
    "title":"FRIENDS"
    },
    {
    "artist":"Dua Lipa",
    "id":10,
    "title":"New Rules"
    },
    {
    "artist":"Shawn Mendes",
    "id":11,
    "title":"In My Blood"
    },
    {
    "artist":"Post Malone",
    "id":12,
    "title":"Psycho"
    },
    {
    "artist":"Ariana Grande",
    "id":13,
    "title":"No Tears Left To Cry"
    },
    {
    "artist":"Bruno Mars",
    "id":14,
    "title":"Finesse"
    },
    {
    "artist":"Kendrick Lamar",
    "id":15,
    "title":"All The Stars"
    },
    {
    "artist":"G-Eazy",
    "id":16,
    "title":"Him & I"
    },
    {
    "artist":"Lauv",
    "id":17,
    "title":"I Like Me Better"
    },
    {
    "artist":"NF",
    "id":18,
    "title":"Let You Down"
    },
    {
    "artist":"Dua Lipa",
    "id":19,
    "title":"IDGAF"
    },
    {
    "artist":"Taylor Swift",
    "id":20,
    "title":"Delicate"
    },
    {
    "artist":"Calvin Harris",
    "id":21,
    "title":"One Kiss"
    },
    {
    "artist":"Ed Sheeran",
    "id":22,
    "title":"Perfect"
    },
    {
    "artist":"Meghan Trainor",
    "id":23,
    "title":"No Excuses"
    },
    {
    "artist":"Niall Horan",
    "id":24,
    "title":"On The Loose"
    },
    {
    "artist":"Halsey",
    "id":25,
    "title":"Alone"
    },
    {
    "artist":"Charlie Puth",
    "id":26,
    "title":"Done For Me"
    },
    {
    "artist":"Foster The People",
    "id":27,
    "title":"Sit Next to Me"
    },
    {
    "artist":"Max",
    "id":28,
    "title":"Lights Down Low"
    },
    {
    "artist":"Alice Merton",
    "id":29,
    "title":"No Roots"
    },
    {
    "artist":"5 Seconds Of Summer",
    "id":30,
    "title":"Want You Back"
    },
    {
    "artist":"Camila Cabello",
    "id":31,
    "title":"Havana"
    },
    {
    "artist":"Logic",
    "id":32,
    "title":"Everyday"
    },
    {
    "artist":"Drake",
    "id":33,
    "title":"Nice For What"
    },
    {
    "artist":"Halsey",
    "id":34,
    "title":"Bad At Love"
    },
    {
    "artist":"ZAYN",
    "id":35,
    "title":"Let Me"
    },
    {
    "artist":"Khalid",
    "id":36,
    "title":"Love Lies"
    },
    {
    "artist":"Post Malone",
    "id":37,
    "title":"rockstar"
    },
    {
    "artist":"Rudimental",
    "id":38,
    "title":"These Days"
    },
    {
    "artist":"Liam Payne",
    "id":39,
    "title":"Familiar"
    },
    {
    "artist":"Imagine Dragons",
    "id":40,
    "title":"Thunder"
    }
    ]
    }


**add song 13 to carl's playlist**

    curl -X POST \
    -d '{"auth_token": "carl", "playlist": 8, "user": "carl", "song": 13}' \
    http://35.166.169.63/playlist_songs \
    --header "Content-Type:application/json"
    
    return code: 200
    return json:
    {
    "status":"ok",
    "data":"song added to playlist"
    }


**add song 15 to carl's playlist**

    curl -X POST \
    -d '{"auth_token": "carl", "playlist": 8, "user": "carl", "song": 15}' \
    http://35.166.169.63/playlist_songs \
    --header "Content-Type:application/json"
    
    return code: 200
    return json:
    {
    "status":"ok",
    "data":"song added to playlist"
    }


**list songs in playlist 8 should see 13 and 15**

    curl -X GET \
    -d '{"auth_token": "carl", "playlist": 8, "user": "carl"}' \
    http://35.166.169.63/playlist_songs \
    --header "Content-Type:application/json"
    return code: 200
    return json:
    {
    "status":"ok",
    "data":[
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


**share playlist 8 with alice**

    curl -X POST \
    -d '{"auth_token": "carl", "playlist": 8, "user": "carl", "share_with": "alice"}' \
    http://35.166.169.63/share \
    --header "Content-Type:application/json"
    
    return code: 200
    return json:
    {
    "status":"ok",
    "data":"playlist shared"
    }


**get full data dump for carl - should be sharing playlist 8**

    curl -X GET \
    -d '{"auth_token": "carl", "user": "carl"}' \
    http://35.166.169.63/debug \
    --header "Content-Type:application/json"
    
    return code: 200
    return json:
    {
    "status":"ok",
    "data":{
    "playlist_shared_with_user":[],
    "playlists":[
    {
    "shared_to":[
    "alice"
    ],
    "playlist_id":8,
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
    "name":"carl",
    "id":18
    }
    }
    }

**get full data dump for alice - should see id 8 being shared**

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
    "playlist_id":8,
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
    "id":17
    }
    }
    }


**carl deletes song 13 from playlist 8**

    curl -X DELETE \
    -d '{"auth_token": "carl", "playlist": 8, "user": "carl", "song": 13}' \
    http://35.166.169.63/playlist_songs \
    --header "Content-Type:application/json"
    
    return code: 200
    return json:
    {
    "status":"ok",
    "data":"song removed from playlist"
    }


**alice can't see the song anymore**

    curl -X GET \
    -d '{"auth_token": "alice", "playlist": 8, "user": "alice"}' \
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


**carl sees all the users he is sharing playlist 8 with**

    curl -X GET \
    -d '{"auth_token": "carl", "playlist": 8, "user": "carl"}' \
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


**carl unshares playlist 8**

    curl -X DELETE \
    -d '{"unshare_with": "alice", "auth_token": "carl", "playlist": 8, "user": "carl"}' \
    http://35.166.169.63/share \
    --header "Content-Type:application/json"
    
    return code: 503
    return json:
    {
    "error":"server error"
    }


**get full data dump for alice - should no shares**

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
    "playlist_id":8,
    "songs":[
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
    "id":17
    }
    }
    }


**carl deletes playlist 8**

    curl -X DELETE \
    -d '{"auth_token": "carl", "playlist": 8, "user": "carl"}' \
    http://35.166.169.63/playlist \
    --header "Content-Type:application/json"
    
    return code: 200
    return json:
    {
    "status":"ok",
    "data":"playlist deleted"
    }

**get full data dump for carl - should have no playlist**

    curl -X GET \
    -d '{"auth_token": "carl", "user": "carl"}' \
    http://35.166.169.63/debug \
    --header "Content-Type:application/json"
    
    return code: 200
    return json:
    {
    "status":"ok",
    "data":{
    "playlist_shared_with_user":[],
    "playlists":[],
    "user":{
    "name":"carl",
    "id":18
    }
    }
    }


**deleting user**

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


**deleting user**

    curl -X DELETE \
    -d '{"auth_token": "carl", "user": "carl"}' \
    http://35.166.169.63/user \
    --header "Content-Type:application/json"
    
    return code: 200
    return json:
    {
    "status":"ok",
    "data":"user deleted"
    }







