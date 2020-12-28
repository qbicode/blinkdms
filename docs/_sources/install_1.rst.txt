Install
#######

OTS software
************

Linux
=====

- Debian 10

install small helper packages:

.. code-block:: bash

    apt install openssh-server
    apt install zip


.. include:: install_postgres.rst



OpenOffice
==========

* needed for conversion docx to pdf
* use program lowriter in the application


.. code-block:: bash

    # size: 480MB
    apt install default-jre
    
    # size: 390MB
    apt install libreoffice-java-common
    
    # size: 50MB
    apt install --no-install-recommends  libreoffice-writer 

    # test, if java and lowriter are installed
    java -version
    # output: e.g. openjdk version "11.0.9.1" 2020-11-04
    
    lowriter --version
    # output: e.g. LibreOffice 6.1.5.2 10(Build:2)
    
    # example convert
    lowriter --convert-to pdf TR_20200709_Agarosebeads.docx


Python + Modules
================

.. hlist::
  :columns: 1
  
  * minimum version: Python3.7
  * python3-pip (use: pip3)
  * Currently: no virtualenv !
  
**Check Python version**

.. code-block:: bash

    python3 --version
    # expected output: Python 3.7.3
    
    # Pip (250 MB)
    apt install python3-pip
    
    # check version
    pip3 --version
    # output: pip 18.1 
  
Install Pip modules:

.. code-block:: bash

    pip3 install jsonrpcclient jsonrpcserver requests Flask  Flask-Session Flask-mail psycopg2 ldap3 python-docx
    
    # upgrade needded for ldpa3
    pip3 install --upgrade pyasn1

More details to the modules:

.. hlist::
  :columns: 1

  * jsonrpcclient (for gozilla_jsonrpc)
  * jsonrpcserver (for JSONRPC) https://jsonrpcserver.readthedocs.io/en/latest
  * requests (for gozilla_jsonrpc)
  * Flask
  * Flask-Session (for extented session)
  * Flask-mail (for emails)
  * psycopg2 (postgres, need apt-get package: libpq-dev)
  * ldap3    (since 2020-03)
  * python-docx (for fOffice document convert)
  
  

.. include:: install_nginx.rst

Application developed software
*******************************

Install system code
===================

Modify permissions for  /usr/bin/lowriter

.. code-block:: bash

    chown -R www-data:www-data  /var/www


Create data directories

.. code-block:: bash

    mkdir /data/blinkdms
    mkdir /data/blinkdms/docs
    mkdir /data/blinkdms/work
    chown -R www-data:www-data /data/blinkdms

Resource: GIT_PROJECT=TBD!

copy code from [GIT_PROJECT]/blinkdms to /opt/blinkdms/blinkdms

.. code-block:: bash

     chown -R www-data:www-data /opt/blinkdms/blinkdms


Postgres: database schema
=========================

.. include:: install_postgres_schema.rst


..
   COMMENT: Python code
  
.. include::  install_2.rst

First login to the system
=========================

  * go to the web browser; url: x.x.x.x:8080  (depending on your nginx config)
  * login as root, password: nopasswd
  * go to user settings and change the initial password !
  * go the the Admin area
  * run the plugin "System Check"

