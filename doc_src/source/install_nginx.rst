Webserver uWSGI + Nginx
=======================


Install-Source: https://www.digitalocean.com/community/tutorials/
	how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04 

Source as PDF: see [WebSrvInstall]

uWSGI (dynamic)
---------------

Install

.. code-block:: bash

    apt install  libssl-dev


The application provides dynamic HTML pages.

Nginx (static)
--------------

The application provides static HTML pages.

Install procedure
-----------------

.. code-block:: bash

    #
    # install uWSGI + NGINX
    #

    # PATH: /opt/blinkdms/blinkdms
    /var/log/daemon.log

    # UFW
    %  apt install ufw


    ### NGINX ##
    # see https://www.digitalocean.com/community/tutorials/
          how-to-install-nginx-on-ubuntu-18-04
    % apt install nginx

    # firewall: if needed TBD: ask your network admin
    % ufw allow 'Nginx HTTP'

    % systemctl stop nginx
    % systemctl start nginx
    # reload: systemctl reload nginx
    # check NGINX
    %systemctl status nginx
    
No create a file /etc/nginx/sites-available/blinkdms

Content: 

  * If you want to set a server-name add option: server_name  YOUR_LAN YOUR_HOST_NAME;
  * Please set your YOUR_HOST_NAME, set YOUR_LAN: e.g. blink.lan)

.. code-block:: bash

    server {
        listen 8080;
        listen [::]:8080;

        location / {
            include uwsgi_params;
            uwsgi_pass unix:/opt/blinkdms/blinkdms/app.sock;
        }

    }
    
    
Continue configuration
    
.. code-block:: bash
    
    # copy config to sites-enabled
    ln -s /etc/nginx/sites-available/blinkdms /etc/nginx/sites-enabled
    # test config
    nginx -t
    
 

Install uWSGI
    
.. code-block:: bash 

    pip3 install uwsgi 
   


create a system service file /etc/systemd/system/blinkdms.service

.. code-block:: bash

    [Unit]
    Description=uWSGI instance to serve blinkdms
    After=network.target

    [Service]
    User=www-data
    Group=www-data

    WorkingDirectory=/opt/blinkdms/blinkdms
    ExecStart=/usr/local/bin/uwsgi --ini app.ini

    [Install]
    WantedBy=multi-user.target

Continue with uwsgi starting

.. code-block:: bash

    # create user if NOT exists
    # important: the user needs a home and a shell 
    #    for PDF convert of command lowriter !!!
    
    # if www-data not exists ...
    # useradd -m www-data
    # Whats this ??? ...
    # sudo passwd www-data

    # IMPORTANT: nginx and uwsgi will be started later after installing the python-code ...

    # useful commands

    systemctl restart nginx
    systemctl stop blinkdms
    systemctl start blinkdms
    systemctl restart blinkdms
    systemctl status blinkdms
    tail /var/log/daemon.log
    tail /var/log/nginx/error.log

    # logs ..
    less /var/log/nginx/error.log: checks the Nginx error logs.
    less /var/log/nginx/access.log: checks the Nginx access logs.
    # checks the Nginx process logs
    journalctl -u nginx
    # checks your Flask app's uWSGI logs.
    journalctl -u blinkdms 
  
  
**SSL on NGINX**

Info from:  https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-in-ubuntu-18-04
    
.. code-block:: bash    

    % sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048  
       -keyout /etc/ssl/private/nginx-selfsigned.key 
       -out /etc/ssl/certs/nginx-selfsigned.crt

    Country Name (2 letter code) [AU]:DE
    State or Province Name (full name) [Some-State]:Thuringia
    Locality Name (eg, city) []:Jena
    Organization Name (eg, company) [Internet Widgits Pty Ltd]:YOUR_COMPANY
    Organizational Unit Name (eg, section) []:IT
    Common Name (e.g. server FQDN or YOUR name) []:YOUR_SERVER_NAME
    Email Address []:your@email-address

    #  create a strong Diffie-Hellman group, 
    % openssl dhparam -out /etc/nginx/dhparam.pem 4096

    # Creating a Configuration Snippet Pointing to the SSL Key and Certificate
    % sudo nano /etc/nginx/snippets/self-signed.conf

    # Creating a Configuration Snippet with Strong Encryption Settings
    % nano /etc/nginx/snippets/ssl-params.conf

    # mod /etc/nginx/sites-available/blinkdms

    # enabled changes on NGINX 
    % nginx -t
    # see warnings
    Output
    nginx: [warn] "ssl_stapling" ignored, issuer certificate not found
    nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    nginx: configuration file /etc/nginx/nginx.conf test is successful

    # restart
    % systemctl restart nginx



Multiple Webservers
-------------------

Introdution:

* Goal: run multiple instances of the application with different databases.
* blinkdms_dev runs only HTTP protocol (no SSL)


Actions:

.. code-block:: bash

    # copy /etc/nginx/sites-available/blinkdms+ to new config blinkdms_dev
    # modify blinkdms_dev
    % ln -s /etc/nginx/sites-available/... /etc/nginx/sites-enabled
    # copy the python-code from /opt/blinkdms to /opt/blinkdms_dev
    # change GROUP ownership of /opt/blinkdms_dev/blinkdms
    chmod g+w blinkdms  
    chgrp www-data blinkdms/app.sock
    chmod g+w blinkdms/app.sock

    # modify /opt/blinkdms_dev/app.ini
    # create new /etc/systemd/system/blinkdms_dev.service (see example below)
    # modify app-config /opt/blinkdms_dev/blinkdms/conf/config.py

    # reload system configs
    % systemctl daemon-reload
    # restart Nginx + uWSGI
    % systemctl restart nginx
    % systemctl restart blinkdms_dev







Example for /etc/systemd/system/blinkdms_dev.service:

.. code-block:: bash

    [Unit]
    Description=uWSGI instance to serve blinkdms_dev
    After=network.target

    [Service]
    User=www-data
    Group=www-data

    WorkingDirectory=/opt/blinkdms_dev/blinkdms
    ExecStart=/usr/local/bin/uwsgi --ini app.ini

    [Install]
    WantedBy=multi-user.target

