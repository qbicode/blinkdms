..
  comment: maintenance postgres

Postgres: maintenance
=====================


**Scope:** maintain the the database

Export a full database
----------------------

**Create Dump**


.. code-block:: bash

    # --no-owner no ownership in output
    pg_dump dmsdb --file=/data/postgresql/dumps/2019-05-08.dump.sql 
       --format=plain --encoding=UTF8 --schema=blinkdms_tab   
       -x --no-tablespaces --no-owner

Restore a dump 
--------------

Scope: restore a dump for an existing DB-user

  * delete old data of DB-user
  * create new database table
  * import DUMP
  
delete old data:

.. code-block:: bash
 
    psql -d dmsdb
    sql> DROP SCHEMA blinkdms_tab cascade;
    sql> REASSIGN OWNED BY blinkdms TO postgres;
    sql> DROP OWNED BY blinkdms;
    sql> DROP USER blinkdms;
    sql> DROP ROLE blinkdms_user;
    sql> exit;
 
now recreate the DB user + tablespace:

.. code-block:: bash
 
    psql -d dmsdb -v ON_ERROR_STOP=1 
      < /opt/blinkdms/blinkdms/install/sql/create_user.sql
      
import:

.. code-block:: bash

    psql -v ON_ERROR_STOP=1 -d dmsdb -U blinkdms  
      < /data/postgresql/dumps/YOUR_DUMP.sql