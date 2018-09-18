USER=highspot
GROUP=highspot

# remove database if exists
if [ -e db/playlist.sqlite ]; then
    rm db/playlist.sqlite
fi

# reload schema
sqlite3 db/playlist.sqlite < db/schema.sql

# load data
python db/dataloader.py

chown -R $USER:$GROUP db

# jump right into sqlite to check database manually
##sqlite3 db/playlist.sqlite

