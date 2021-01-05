..
   COMMENT own developed PYTHON code

Python-Code
===========

Prerequisites: the code is installed on /opt/blinkdms/blinkdms (see section "Install system code")

Resource:

  * [PYTHON_SRC_DIR]=/opt/blinkdms/blinkdms
  

Code post config 
----------------

make  app.sock wriuteable for www-data

.. code-block:: bash   

    chgrp www-data /opt/blinkdms/blinkdms
    chmod g+w /opt/blinkdms/blinkdms
    touch /opt/blinkdms/blinkdms/app.sock
    chgrp www-data /opt/blinkdms/blinkdms/app.sock
    chmod g+w /opt/blinkdms/blinkdms/app.sock

Link sources for Admin:

.. code-block:: bash    

    cd /opt/blinkdms/blinkdms
    ln -s /opt/blinkdms/blinkdms/ADM/templates /opt/blinkdms/blinkdms/templates/ADM
    ln -s /opt/blinkdms/blinkdms/ADM/static /opt/blinkdms/blinkdms/static/ADM




Start Web server

.. code-block:: bash   
 
    # start nginx
    systemctl restart nginx
    
    
    systemctl daemon-reload
    
    # allow start of the daemon on system start ...
    systemctl enable blinkdms.service
    
    systemctl restart blinkdms

  
Test a python script 
--------------------

if you want to test a python script on command line you first have to do taht:

.. code-block:: bash   

    export PYTHONPATH=/opt/blinkdms/