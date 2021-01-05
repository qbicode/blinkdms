..
  comment: CREATE postgres schema


**Scope:** Create the magasin-database-schema

Resources:
  * /opt/blinkdms/blinkdms/conf/config.py
  * [SQL_SRC_DIR]=/opt/blinkdms/blinkdms/install/sql
 
Actions: 
  
.. code-block:: bash

    # login as database root and create database
    su -s /bin/bash postgres
    createdb dmsdb
    exit 
    
    # now you are root again



**create user, tablespace, schema and initial data**

  * check, if config_entry [db"]["main"]  exists in /opt/blinkdms/blinkdms/conf/config.py
  * give a password for option --app_root_pw

.. code-block:: bash

  python3 /opt/blinkdms/blinkdms/install/scripts/db_manage.py --create 
        --config_entry "main" --app_root_pw "XXX"


Just in case you have to delete this complete database schema + user: call this command line

.. code-block:: bash

  python3 /opt/blinkdms/blinkdms/install/scripts/db_manage.py --delete --dbuser "blinkdms" 
  

**login**

.. code-block:: bash
  
  su - postgres
  psql -d dmsdb -U blinkdms 
  select * from DB_USER;
    
   

More tutorials for postgres + Python: 
https://medium.com/@gitaumoses4/python-and-postgresql-without-orm-6e9d7fc9a38e

