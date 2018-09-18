
#-----------------------------------------------------------
# configuration and setup
#-----------------------------------------------------------
BASE="/highspot"
USER='highspot'
GROUP='highspot'

mod_wsgi-express setup-server $BASE/app/playlist.wsgi --port=80 \
    --user $USER --group $GROUP \
    --server-root=/tmp/mod_wsgi-express-80

#-----------------------------------------------------------
# start the apache server
#-----------------------------------------------------------
cd /tmp/mod_wsgi-express-80
./apachectl start
