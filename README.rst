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

How to setup for usage
------------------------

Clone Repository

.. code-block:: console

    $ git clone https://github.com/romatt/exseas_explorer.git
    $ cd exseas_explorer

a) Set up a new python virtual environment using venv & pip

.. code-block:: console

    $ python3 -m venv <YOUR_VENV_DIR>
    $ source <YOUR_VENV_DIR>/bin/activate
    $ pip install -U tox-travis
    $ python -m pip install -r requirements.txt
    $ pytest

b) Set up a new python virtual environment using pyenv & poetry

.. code-block:: console

    $ pyenv install 3.9.12
    $ pyenv global 3.9.12
    $ poetry shell
    $ poetry install --no-dev
    $ pytest

How to setup for development
----------------------------

a) Using venv & pip

.. code-block:: console

    $ # Follow the steps described above
    $ python -m pip install -r requirements_dev.txt

b) Using poetry 

.. code-block:: console

    $ # Follow the steps described above
    $ poetry install --no-dev

Update requirements file needed for installing this library with pip

.. code-block:: console

    $ poetry export -f requirements.txt --output requirements.txt --without-hashes
    $ poetry export -f requirements.txt --output requirements_dev.txt --without-hashes --dev

Update documentation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    $ cd doc
    $ make html

Running dash app locally 
------------------------

.. code-block:: console

    $ python exseas_explorer/app.py


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
