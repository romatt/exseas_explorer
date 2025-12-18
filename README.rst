========================
Extreme Seasons Explorer
========================

INTEXseas Extreme Seasons Explorer

* Free software: MIT license

Setup for production
---------------------

1. Clone Repository directly to `/var/www/` or any directory that the web server has access to

   .. code-block:: console

       $ cd /var/www/
       $ git clone https://github.com/romatt/exseas_explorer.git

2. Set up permissions

   .. code-block:: console

       $ cd /var/www/
       $ sudo chown -R www-data:www-data exseas_explorer
       $ cd exseas_explorer

3. Manually copy the raw data into the /data sub-directory of the library

4. Ensure _poetry_ is installed.

5. Set up a new Python virtual environment where all required libraries are installed.

   NOTE: when using apache's _mod_wsgi_ the system python installation _must_ be used (however, a virtual environment is fine)

   .. code-block:: console

       $ python3.12 -m venv /opt/venv/intexseas_py312
       $ source /opt/venv/intexseas_py312/bin/activate
       $ poetry sync --without=dev

5. Install the mod_wsgi Apache module for Python 3

   .. code-block:: console

       $ sudo apt install libapache2-mod-wsgi-py3

6. The apache configuration needs to contain the virtual environment directory

   .. code-block:: ApacheConf

       VirtualHost *:80>
               ServerName intexseas-explorer.ethz.ch

               # commented because of LetsEncrypt bug uncomment in vhost.intexseas-explorer_ethz_ch-le-ssl.conf
               #WSGIDaemonProcess intexseas processes=4 locale=en_US.UTF-8 python-home=/opt/venv/intexseas
               #WSGIProcessGroup intexseas
               #WSGIApplicationGroup %{GLOBAL}

               #WSGIScriptAlias / /var/www/exseas_explorer/exseas_explorer/FlaskApp.wsgi

               ErrorLog "logs/intexseas-explorer.ethz.ch-error_log"
               LogLevel warn
               CustomLog "logs/intexseas-explorer.ethz.ch-access.log" combined

               #<Directory "/var/www/exseas_explorer/exseas_explorer">
               #       Order allow,deny
               #       Allow from all
               #</Directory>

               RewriteEngine on
               RewriteCond %{SERVER_NAME} =intexseas-explorer.ethz.ch
               RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]

       </VirtualHost>

7. Reload Apache

   .. code-block:: console

       $ sudo service apache2 restart

Setup for development
---------------------

1. Clone Repository

   .. code-block:: console

       $ git clone https://github.com/romatt/exseas_explorer.git
       $ cd exseas_explorer

2. Setup virtual environment

   - **EITHER** set up a new python virtual environment using venv & pip

   .. code-block:: console

       $ python3 -m venv <YOUR_VENV_DIR>
       $ source <YOUR_VENV_DIR>/bin/activate
       $ pip install -U tox-travis
       $ python -m pip install -r requirements_dev.txt
       $ pytest

   - **OR** Set up a new python virtual environment using pyenv & poetry

   .. code-block:: console

       $ pyenv install 3.12.8
       $ pyenv global 3.12.8
       $ poetry env use 3.12
       $ poetry shell
       $ poetry install --all-extras
       $ pytest

Running dash application locally
--------------------------------

For testing purposes, the dash application can be run locally on port 8050. If port 8050 is not available, change the port specified at the very bottom of `exseas_explorer\app.py`.

.. code-block:: console

    $ python exseas_explorer/app.py

or from poetry:

.. code-block:: console

    $ poetry run python exseas_explorer/app.py

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
