#!/bin/bash

# ------------------------------------------------------------------------------------------------
# you may need to uncomment the following if installing on ubuntu to ensure the needed
# libraries have been installed
# ------------------------------------------------------------------------------------------------

#apt-get install libreadline-gplv2-dev \
#                libncursesw5-dev \
#                libssl-dev \
#                libsqlite3-dev \
#                tk-dev \
#                libgdbm-dev \
#                libc6-dev libbz2-dev

# ------------------------------------------------------------------------------------------------
# configuration
# ------------------------------------------------------------------------------------------------

BASE=/highspot
TARBALLS=$BASE/src/tarballs
SOURCES=$BASE/src/sources
INSTALLTO=$BASE/bin

# ------------------------------------------------------------------------------------------------
# install user
# ------------------------------------------------------------------------------------------------
function create_users()
{
    id -u highspot &>/dev/null || useradd -p password highspot
}

# ------------------------------------------------------------------------------------------------
# get sources
# ------------------------------------------------------------------------------------------------

# if not already downloaded, go and get
function getsource()
{
    local url=$1
    if [[ $url =~ .*\/(.*) ]]
    then
        local filename=$(basename $url)
        if [[ ! -f $TARBALLS/$filename ]]; then
            wget $url -P $TARBALLS
        fi
    fi
}

# ------------------------------------------------------------------------------------------------
# prep directory
# ------------------------------------------------------------------------------------------------
function prep_directories()
{
    mkdir -p $TARBALLS
    mkdir -p $SOURCES
    getsource "http://apache.claz.org/apr/apr-1.6.3.tar.gz"
    getsource "http://mirror.olnevhost.net/pub/apache/apr/apr-util-1.6.1.tar.gz"
    getsource "http://apache.cs.utah.edu//httpd/httpd-2.4.34.tar.gz"
    getsource "https://www.python.org/ftp/python/2.7.13/Python-2.7.13.tgz"
    getsource "https://bootstrap.pypa.io/get-pip.py"
    getsource "https://files.pythonhosted.org/packages/9e/37/dd336068ece37c43957aa337f25c59a9a6afa98086e5507908a2d21ab807/mod_wsgi-4.6.4.tar.gz"

}

# ------------------------------------------------------------------------------------------------
# installed and in path
# ------------------------------------------------------------------------------------------------
function is_installed()
{
    local fullpath=$1
    local filename=$(basename $fullpath)
    if [[ $(which $filename) =~ "$fullpath" ]]
    then
        echo "true"
    else
        echo "false"
   fi
}

# ------------------------------------------------------------------------------------------------
# update path and bashrc
# ------------------------------------------------------------------------------------------------
function update_path
{
    path=$1
    if ! grep -q "export\ PATH\=$path" ~/.bashrc
    then
           echo "found"
           echo "export PATH=$path:\$PATH" >> ~/.bashrc
    fi
    export PATH=$path:$PATH
}

# ------------------------------------------------------------------------------------------------
# unpack
# ------------------------------------------------------------------------------------------------

# uncompresses if not already done
# if already uncompressed then make clean for next compile

function unpack_or_clean()
{
    if [ "$1" = "true" ]
    then
        rm -rf $SOURCES/*
    fi

    for file in `ls $TARBALLS`; do
        if [[ $file =~ (.*)\.tar\.gz || $file =~ (.*)\.tgz ]]; then
            dirname=${BASH_REMATCH[1]}
            if [[ -d $SOURCES/$dirname ]];
            then
                cd $SOURCES/$dirname
                echo make clean $dirname
                make clean
            else
                tar -zxvf $TARBALLS/$file -C $SOURCES
            fi
        else
            cp -arv $TARBALLS/$file $SOURCES
        fi
    done
}

# ------------------------------------------------------------------------------------------------
# install apache
# ------------------------------------------------------------------------------------------------
function install_apache()
{

    if [ "$1" = "true" ]
    then
        if [[ $(is_installed $INSTALLTO/apache2/bin/apachectl) == "true" ]]
        then
            apachectl stop
        fi
        rm -rf $INSTALLTO/apache2
    fi

    update_path $INSTALLTO/apache2/bin

    if [[ $(is_installed $INSTALLTO/apache2/bin/apachectl) == "false" ]]
    then
        mkdir -p $SOURCES/httpd-2.4.34/srclib/apr
        mkdir -p $SOURCES/httpd-2.4.34/srclib/apr-util
        rm -rf $SOURCES/httpd-2.4.34/srclib/apr/*
        rm -rf $SOURCES/httpd-2.4.34/srclib/apr-util/*
        cp -arv  $SOURCES/apr-1.6.3/* $SOURCES/httpd-2.4.34/srclib/apr
        cp -arv  $SOURCES/apr-util-1.6.1/*  $SOURCES/httpd-2.4.34/srclib/apr-util

        cd $SOURCES/httpd-2.4.34
        ./configure --prefix=$INSTALLTO/apache2 --with-included-apr
        make
        make install

        if [[ ! $(is_installed $INSTALLTO/apache2/bin/apachectl) == "true" ]]
        then
            echo "*** apache install error ***"
            exit 1
        fi
    fi
}

# ------------------------------------------------------------------------------------------------
# install python
# ------------------------------------------------------------------------------------------------
function install_python()
{
    if [ "$1" = "true" ]
    then
        rm -rf $INSTALLTO/python-2.7.13
    fi

    update_path $INSTALLTO/python-2.7.13/bin

    if [[ $(is_installed $INSTALLTO/python-2.7.13//bin/python) == "false" ]]
    then
        cd $SOURCES/Python-2.7.13
        ./configure --enable-shared --prefix=$INSTALLTO/python-2.7.13 LDFLAGS=-Wl,-rpath=$INSTALLTO/python-2.7.13/lib
        make
        make install

        # verify everything installed correctly
        if [[ $(is_installed $INSTALLTO/python-2.7.13/bin/python) == "false" ]]
        then
            echo "*** python install error **"
            exit 1
        fi
    fi
}

# ------------------------------------------------------------------------------------------------
# install pip
# ------------------------------------------------------------------------------------------------
function install_pip()
{

    if [ "$1" = "true" ]
    then
        rm -rf $INSTALLTO/python-2.7.13/bin/pip
    fi

    if [[ $(is_installed $INSTALLTO/python-2.7.13/bin/pip) == "false" ]]
    then
        cd $SOURCES
        python get-pip.py

        # verify everything installed correctly
        if [[ $(is_installed $INSTALLTO/python-2.7.13/bin/pip) == "false" ]]
        then
            echo "** pip install error  **"
            exit 1
        fi
    fi
}

# ------------------------------------------------------------------------------------------------
# install mod_wsgi
# ------------------------------------------------------------------------------------------------
function install_wsgi()
{

    if [ "$1" = "true" ]
    then
        pip uninstall -y mod_wsgi
    fi

    if [[ $(is_installed $INSTALLTO/python-2.7.13/bin/mod_wsgi-express) == "false" ]]
    then
        export APXS=$INSTALLTO/apache2/bin/apxs
        #export MOD_WSGI_MODULES_DIRECTORY=$INSTALLTO/apache2/modules
        pip install mod_wsgi

        mod_wsgi-express start-server --user highspot --group highspot

        if [[ $(is_installed $INSTALLTO/python-2.7.13/bin/mod_wsgi-express) == "false" ]]
        then
            echo "** wsgi install error **"
            exit 1
        fi
    fi
}

function install_libs()
{
    if [ "$1" = "true" ]
    then
        pip uninstall -y werkzeug
    fi

    pip install werkzeug
    pip install dataset
    pip install cachetools
    pip install unittest2
    pip install requests
}


# ------------------------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------------------------

if [ $# -eq 0 ]
  then
      echo "Usage: install.sh [--force] --all | --apache | --python | --wsgi | --libs"
      echo "  --force     force install"
      echo "  --all       install everything"
      echo "  --apache    install apache"
      echo "  --python    install python"
      echo "  --wsgi      install mod_wsgi"
      echo "  --libs      install python libraries"
fi

create_users
prep_directories


for arg in "$@";
do
  shift
  case "$arg" in
      "--force")
          FORCE=true
          ;;
      "--all")
          unpack_or_clean $FORCE
          install_apache $FORCE
          install_python $FORCE
          install_pip $FORCE
          install_wsgi $FORCE
          install_libs
          exit;
          ;;
      "--apache")
          unpack_or_clean $FORCE
          install_apache $FORCE
          exit;
          ;;
      "--python")
          unpack_or_clean $FORCE
          install_python $FORCE
          install_pip $FORCE
          exit;
          ;;
      "--wsgi")
          install_wsgi $FORCE
          ;;
      "--libs")
          install_libs $FORCE
          ;;
      esac

done
# ------------------------------------------------------------------------------------------------
exit 0
# ------------------------------------------------------------------------------------------------
