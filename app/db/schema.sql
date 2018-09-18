
PRAGMA foreign_keys=ON;

-----------------------------------------------------------------------
-- tables
-----------------------------------------------------------------------
CREATE TABLE "user"
(
       "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL ,
       "name" TEXT NOT NULL,

	CONSTRAINT name_constraint UNIQUE(name)
 );



CREATE TABLE "song"
(
       "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL ,
       "artist_id" INTEGER NOT NULL,
       "title" TEXT NOT NULL,

	FOREIGN KEY(artist_id) references artist(id)
	CONSTRAINT title_constraint UNIQUE(artist_id, title)
);


CREATE INDEX song_artist_id on song(artist_id);


CREATE TABLE "playlist"
(
       "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL ,
       "user_id" TEXT NOT NULL,

	FOREIGN KEY(user_id) references user(id)
 );

CREATE INDEX playlist_user_id on playlist(user_id);



CREATE TABLE "playlist_x_song"
(
       "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL ,
       "playlist_id" INTEGER NOT NULL,
       "song_id" INTEGER NOT NULL,

	FOREIGN KEY(playlist_id) references playlist(id)
        FOREIGN KEY(song_id) references song(id)

);

CREATE INDEX playlistx_playlist_id on playlist_x_song(playlist_id);
CREATE INDEX playlistx_song_id on playlist_x_song(song_id);


CREATE TABLE "artist"
(
       "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL ,
       "artist" TEXT NOT NULL,

	CONSTRAINT artist_constraint UNIQUE(artist)
);

CREATE TABLE "shared"
(
        "id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL,
        "playlist_id" INTEGER NOT NULL,
        "shared_to_user_id" INTEGER NOT NULL,

	FOREIGN KEY(playlist_id) references playlist(id)
        FOREIGN KEY(shared_to_user_id) references user(id)
);

CREATE INDEX shared_playlist_id on shared(playlist_id);
CREATE INDEX shared_user_id on shared(shared_to_user_id);

-----------------------------------------------------------------------
-- triggers
-----------------------------------------------------------------------

 CREATE TRIGGER delete_user
 AFTER DELETE on user
 FOR EACH ROW
 BEGIN
     DELETE FROM playlist where playlist.user_id = OLD.id;
     DELETE FROM shared where shared.shared_to_user_id = OLD.id;
 END;


 CREATE TRIGGER delete_playlist
 AFTER DELETE on playlist
 FOR EACH ROW
 BEGIN
     DELETE FROM playlist_x_song where playlist_x_song.playlist_id = OLD.id;
     DELETE FROM shared where shared.playlist_id = OLD.id;
 END;
