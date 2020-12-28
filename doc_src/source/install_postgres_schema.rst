..
  comment: CREATE postgres schema


**Scope:** Create the magasin-database-schema

Resources:
  * [SQL_SRC_DIR]=/opt/blinkdms/blinkdms/install/sql
 
Actions: 
  * Change the password for user blinkdms in the file /opt/blinkdms/blinkdms/install/sql/create_user.sql
  * Now login as postgres

.. code-block:: bash

    su -s /bin/bash postgres
    createdb dmsdb

**create user, roles and schema**

.. code-block:: bash

    psql -d dmsdb -v ON_ERROR_STOP=1 
      < /opt/blinkdms/blinkdms/install/sql/create_user.sql

**login**

.. code-block:: bash

    psql -d dmsdb -U blinkdms -W


database - features:

	* Indexing
	* Trigger, Constraints
	* Transaction (ACID)
	* Referential Integrity
	* Security
	* Locking


..
   COMMENT: EXPORT/IMPORT

Import the database schema
--------------------------

**Import Dump**

Location of the SQL-data:  /opt/blinkdms/blinkdms/install/sql/schema_dump.sql

Prerequisites:

  * database, user, roles, schema must exist
  * schema must exists before 
  * dump is in plain text (SQL)
  * the dump must NOT contain schema-table names !!!
  * https://www.postgresql.org/docs/8.4/backup-dump.html



.. code-block:: bash

    psql -v ON_ERROR_STOP=1 -d dmsdb -U blinkdms  
      < /opt/blinkdms/blinkdms/install/sql/schema_dump.sql
      
test success ...

.. code-block:: bash

    psql -d dmsdb -U blinkdms 
    select * from DB_USER;
    
   

More tutorials for postgres + Python: 
https://medium.com/@gitaumoses4/python-and-postgresql-without-orm-6e9d7fc9a38e

