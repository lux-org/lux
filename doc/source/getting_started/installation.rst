************
Installation
************

Lux API is the core Python framework for supporting intelligent data discovery. 
Lux API can be used in conjunction with the Lux widget, which is a frontend Jupyter widget extension built with ipywidget. 

You can install the Python Lux API through `PyPI <https://pypi.org/project/lux-api/>`_

.. code-block:: console

    pip install lux-api

You can install the Lux Jupyter widget through `npm <https://www.npmjs.com/package/lux-widget>`_

.. code-block:: console

    npm i lux-widget

Additional Requirements
-----------------------

If you want to use Lux with a SQL execution engine as a backend, you need to install Postgres (version >= 9.5).
A tutorial on installing PostgresSQL on Mac OSX can be found `here <https://chartio.com/resources/tutorials/how-to-start-postgresql-server-on-mac-os-x/>`_.

In addition to setting up Postgres, you also need to install Psycopg2 for the Python code in Lux to query Postgres database.

.. code-block:: console

    pip install psycopg2

Manual Installation (Dev Setup)
--------------------------------

To setup Lux manually for development purposes, you should clone the two Github repos for Lux: 1) the core Python `Lux API <https://github.com/lux-org/lux>`_  and 2) the `Jupyter widget frontend <https://github.com/lux-org/lux-widget>`_. 

To install the Python Lux API: 

.. code-block:: console

    pip install --user -r requirements.txt
    cd lux/
    python setup.py install

To install the widget, we need to install webpack:  

.. code-block:: console
    
    npm install --save-dev webpack webpack-cli

Then, we can install the `Lux Jupyter widget <https://github.com/lux-org/lux-widget>`_ using the custom installation script: 

.. code-block:: console

    git clone git@github.com:lux-org/lux-widget.git
    cd lux-widget/
    npm install
    bash install.sh

If you are experiencing issues with installing Lux, please checkout the `Troubleshooting page <https://lux-api.readthedocs.io/en/latest/source/guide/FAQ.html#troubleshooting-tips>`_.