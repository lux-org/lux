************
Installation
************

Lux API is the core Python framework for supporting intelligent data discovery. 
Lux API can be used in conjunction with the Lux widget, which is a frontend Jupyter widget extension built with ipywidget. 

You can install the Python Lux API through `PyPI <https://pypi.org/project/lux-api/>`_

.. code-block:: bash

pip install lux-api

You can install the Lux Jupyter widget through `npm <https://www.npmjs.com/package/lux-widget>`_

.. code-block:: bash

npm i lux-widget

Additional Requirements
-----------------------

If you want to use Lux with a SQL execution engine as a backend, you need to install Postgres (version >= 9.5).
A tutorial on installing PostgresSQL on Mac OSX can be found `here <https://chartio.com/resources/tutorials/how-to-start-postgresql-server-on-mac-os-x/>`_.

In addition to setting up Postgres, you also need to install Psycopg2 for the Python code in Lux to query Postgres database.

.. code-block:: bash

pip install psycopg2

Development Setup
-----------------
Instructions forthcoming.
