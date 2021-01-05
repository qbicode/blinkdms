
RDBMS Postgres
==============

The application is based on data transfer with a database service on a remote database server. 
The underlying database model is named **Blinkdms Magasin**.

Database - features:

        * Indexing
        * Trigger, Constraints
        * Transaction (ACID)
        * Referential Integrity
        * Security
        * Locking

main Postgres directories/files:

  * [etc-config-dir] = /etc/postgresql/11/main
  * [PG_DATA_DIR] = /data/postgresql/main
  * [PG_DUMP_DIR] = /data/postgresql/dumps


Install Postgres 11:

.. code-block:: bash

    apt-get install postgresql postgresql-contrib  (118MB)
    apt-get install libpq-dev (for postgres + python)


Docu see https://wiki.debian.org/PostgreSql#Installation


Manage data dir (create data dir \verb+[PG_DATA_DIR]+, move original data dir to this location):

.. code-block:: bash

    mkdir /data/postgresql/main
    chown -R postgres:postgres /data/postgresql/main
    mv /var/lib/postgresql/11/main /data/postgresql/
    
    # create dump dir for export, import, backup
    mkdir /data/postgresql/dumps
    chown -R postgres:postgres /data/postgresql/dumps
   

set configs in etc-config-dir postgresql.conf :
    
.. code-block:: bash
 
    data_directory='/data/postgresql/main'
    SET standard_conforming_strings=on


set AUTHORIZATION in [etc-config-dir]/pg_hba.conf ; change ident to trust !

.. code-block:: bash

    ---
    # TYPE  DATABASE    USER        CIDR-ADDRESS          METHOD

    # "local" is for Unix domain socket connections only
    local   all         all                               trust
    host    all         all         127.0.0.1/32          trust
    # IPv6 local connections:
    host    all         all         ::1/128               trust
    ---



Start DB:

.. code-block:: bash

    systemctl stop postgresql
    systemctl start postgresql

