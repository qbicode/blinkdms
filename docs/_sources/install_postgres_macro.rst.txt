

Modify the INIT-DATA file: 

.. code-block:: bash

    sed --in-place  -e 's/SELECT pg_catalog.set_config.*//' 
     -e 's/blinkdms_tab\.//g'  
     -e 's/CREATE SCHEMA.*//' 2019-10-30.dump.ini_data.sql




