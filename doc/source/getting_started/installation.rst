************
Installation
************

Lux API is the core Python framework for supporting intelligent data discovery. 
Lux API can be used in conjunction with the Lux widget, which is a frontend Jupyter widget extension built with ipywidget. 

You can install the Python Lux API through `PyPI <https://pypi.org/project/lux-api/>`_

.. code-block:: bash

    pip install lux-api

To activate the Jupyter notebook extension: 

.. code-block:: bash

    jupyter nbextension install --py luxwidget
    jupyter nbextension enable --py luxwidget

To activate the JupyterLab extension: 

.. code-block:: bash

    jupyter labextension install @jupyter-widgets/jupyterlab-manager
    jupyter labextension install luxwidget

Additional Requirements
-----------------------

If you want to use Lux with a SQL execution engine as a backend, you need to install Postgres (version >= 9.5).
A tutorial on installing PostgresSQL on Mac OSX can be found `here <https://chartio.com/resources/tutorials/how-to-start-postgresql-server-on-mac-os-x/>`_.

In addition to setting up Postgres, you also need to install Psycopg2 for the Python code in Lux to query Postgres database.

.. code-block:: bash

    pip install psycopg2

Manual Installation (Dev Setup)
--------------------------------

To setup Lux manually for development purposes, you should clone the two Github repos for Lux: 1) the core Python `Lux API <https://github.com/lux-org/lux>`_  and 2) the `Jupyter widget frontend <https://github.com/lux-org/lux-widget>`_. 

To install the Python Lux API: 

.. code-block:: bash

    git clone https://github.com/lux-org/lux.git
    cd lux/
    pip install --user -r requirements.txt
    python setup.py install

To install the widget, we need to install webpack:  

.. code-block:: bash
    
    npm install --save-dev webpack webpack-cli

Then, we can install the `Lux Jupyter widget <https://github.com/lux-org/lux-widget>`_ using the custom installation script: 

.. code-block:: bash

    git clone git@github.com:lux-org/lux-widget.git
    cd lux-widget/
    npm install
    sh install.sh
    sh install_lab.sh

If you are experiencing issues with installing Lux, please checkout the `Troubleshooting page <https://lux-api.readthedocs.io/en/latest/source/guide/FAQ.html#troubleshooting-tips>`_.