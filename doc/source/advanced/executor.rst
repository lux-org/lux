****************
Execution Engine
****************

Fetching the data required for generating visualizations can be computationally expensive, especially on large datasets. Lux provides a extensible framework for users to pick their own execution backend for data processing. We currently support Pandas (default, :mod:`lux.executor.PandasExecutor`) and SQL (:mod:`lux.executor.SQLExecutor`). In this tutorial, we explain how to use switch to SQL as an execution backend, as an example of how you can use a different data processing mechanism in Lux.

Please refer to :mod:`lux.executor.Executor`, if you are interested in extending Lux for your own execution backend.



SQL Executor
=============

Lux extends its visualization exploration operations to data within SQL databases. By using the SQL Executor, users can specify a SQL database to connect a Lux Dataframe for generating all the visualizations recommended in Lux.

Connecting Lux to a Database
----------------------------

Before Lux can operate on data within a Postgresql database, users have to connect their Lux Dataframe to their database.
To do this, users first need to specify a connection to their SQL database. This can be done using the psycopg2 package's functionality.

.. code-block:: python

	import psycopg2
	connection = psycopg2.connect("dbname=example_database user=example_user, password=example_password")

Once this connection is created, users can connect their Lux Dataframe to the database using the Lux Dataframe's setSQLConnection command.

.. code-block:: python

	lux_df.setSQLConnection(connection, "my_table")

When the setSQLConnection function is called, Lux will then populate the Dataframe with all the metadata it needs to run its context from the database table. 

Choosing an Executor
--------------------------

Once a user has created a connection to their Postgresql database, they need to change Lux's execution engine so that the system can collect and process the data properly.
By default Lux uses the Pandas executor to process local data in the Lux Dataframe, but users need to use the SQL executor when their Lux Dataframe is connected to a database.
Users can specify the executor that a Lux Dataframe will use via the setExecutorType function as follows:

.. code-block:: python

	lux_df.setExecutorType("SQL")

Once a Lux Dataframe has been connected to a Postgresql table and set to use the SQL Executor, users can take full advantage of Lux's visual exploration capabilities as-is. Users can set their context to specify which variables they are most interested in and discover insightful visualizations from their database.

SQL Executor Limitations
--------------------------

While users can make full use of Lux's functionalities on data within a database table, they will not be able to use any of Pandas' Dataframe functions to manipulate the data. Since the Lux SQL Executor delegates most data processing to the Postgresql database, it does not pull in the entire dataset into the Lux Dataframe. As such there is no actual data within the Lux Dataframe to manipulate, only the relevant metadata required to for Lux to manage its context. Thus, if users are interested in manipulating or querying their data, this needs to be done through SQL or an alternative RDBMS interface.