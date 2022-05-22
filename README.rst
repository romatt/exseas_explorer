========================
Extreme Seasons Explorer
========================

.. image:: https://img.shields.io/pypi/v/exseas_explorer.svg
        :target: https://pypi.python.org/pypi/exseas_explorer

.. image:: https://img.shields.io/travis/romatt/exseas_explorer.svg
        :target: https://travis-ci.com/romatt/exseas_explorer

.. image:: https://readthedocs.org/projects/exseas-explorer/badge/?version=latest
        :target: https://exseas-explorer.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


INTEXseas Extreme Seasons Explorer


* Free software: BSD license
* Documentation: https://exseas-explorer.readthedocs.io.

Setup for production
---------------------

1. Clone Repository directly to `/var/www/` or any directory that the web server has access to. Additionally, manually copy the raw data into the /data sub-directory.

.. code-block:: console

    $ cd /var/www/
    $ git clone https://github.com/romatt/exseas_explorer.git
    $ cd exseas_explorer
    
2. Set up permissions

.. code-block:: console

    $ cd /var/www/
    $ sudo chown -R www-data:www-data exseas_explorer

3. Set up a new Python virtual environment where all required libraries are installed. Note that the system wide installed Python version must be used to avoid issues with shared libraries (i.e. don't use Python installed through pyenv or it will not work!).

.. code-block:: console

    $ python3 -m venv <YOUR_VENV_DIR>
    $ source <YOUR_VENV_DIR>/bin/activate
    $ pip install -U tox-travis
    $ python -m pip install -r requirements.txt

4. The apache configuration needs to contain the virtual environment directory

.. code-block:: ApacheConf

    <IfModule mod_ssl.c>
            <VirtualHost *:443>
                <VirtualHost *:443>
                    ServerName <URL>
                    SSLEngine On
                    SSLProxyEngine On

                    SSLCertificateFile /etc/letsencrypt/live/<URL>/cert.pem
                    SSLCertificateKeyFile /etc/letsencrypt/live/<URL>/privkey.pem
                    SSLCertificateChainFile /etc/letsencrypt/live/<URL>/chain.pem

                    WSGIDaemonProcess intexseas python-home=<YOUR_VENV_DIR>
                    WSGIProcessGroup intexseas
                    WSGIApplicationGroup %{GLOBAL}
                    WSGIScriptAlias / /var/www/exseas_explorer/exseas_explorer/FlaskApp.wsgi
                    ErrorLog ${APACHE_LOG_DIR}/FlaskApp-error.log
                    LogLevel warn
                    CustomLog ${APACHE_LOG_DIR}/FlaskApp-access.log combined
            </VirtualHost>
    </IfModule>

5. Reload Apache

.. code-block:: console

    $ sudo service apache2 restart

Troubleshooting
~~~~~~~~~~~~~~~~

If you get an Internal Server Error and the Apache2 logs show an `UnicodeDecodeError`

.. code-block:: console

    File "/usr/lib/python3.8/encodings/ascii.py", line 26, in decode
    return codecs.ascii_decode(input, self.errors)[0]
    UnicodeDecodeError: 'ascii' codec can't decode byte 0xc5 in position 375347: ordinal not in range(128)

Simply change uncomment the following line under `/etc/apache2/envvars`

.. code-block:: console

    ## Uncomment the following line to use the system default locale instead:
    . /etc/default/locale

Setup for development
---------------------

Clone Repository

.. code-block:: console

    $ git clone https://github.com/romatt/exseas_explorer.git
    $ cd exseas_explorer

**EITHER** set up a new python virtual environment using venv & pip

.. code-block:: console

    $ python3 -m venv <YOUR_VENV_DIR>
    $ source <YOUR_VENV_DIR>/bin/activate
    $ pip install -U tox-travis
    $ python -m pip install -r requirements_dev.txt
    $ pytest

**OR** Set up a new python virtual environment using pyenv & poetry

.. code-block:: console

    $ pyenv install 3.9.12
    $ pyenv global 3.9.12
    $ poetry shell
    $ poetry install
    $ pytest

Update requirements file needed for installing this library with pip

.. code-block:: console

    $ poetry export -f requirements.txt --output requirements.txt --without-hashes
    $ poetry export -f requirements.txt --output requirements_dev.txt --without-hashes --dev

Running dash application locally 
--------------------------------

For testing purposes, the dash application can be run locally on port 8050. If port 8050 is not available, change the port specified at the very bottom of `exseas_explorer\app.py`.

.. code-block:: console

    $ python exseas_explorer/app.py

Update documentation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    $ cd doc
    $ make html

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
