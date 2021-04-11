****************
Execution Engine
****************

Fetching the data required for generating visualizations can be computationally expensive, especially on large datasets. Lux provides a extensible framework for users to pick their own execution backend for data processing. We currently support Pandas (default, :mod:`lux.executor.PandasExecutor`) and SQL (:mod:`lux.executor.SQLExecutor`). In this tutorial, we explain how to use switch to SQL as an execution backend, as an example of how you can use a different data processing mechanism in Lux.

Please refer to :mod:`lux.executor.Executor`, if you are interested in extending Lux for your own execution backend.



SQL Executor
=============

Lux extends its visualization exploration operations to data within SQL databases. By using the SQL Executor, users can specify a SQL database to connect a LuxSQLTable for generating all the visualizations recommended in Lux.

Connecting Lux to a Database
----------------------------

Before Lux can operate on data within a Postgresql database, users have to connect their LuxSQLTable to their database.
To do this, users first need to specify a connection to their SQL database. This can be done using the psycopg2 package's functionality.

.. code-block:: python

	import psycopg2
	connection = psycopg2.connect("dbname=example_database user=example_user, password=example_password")

Once this connection is created, users can connect the lux config to the database using the set_SQL_connection command.

.. code-block:: python

	lux.config.set_SQL_connection(connection)

When the set_SQL_connection function is called, Lux will then populate the LuxSQLTable with all the metadata it needs to run its intent from the database table. 

Connecting a LuxSQLTable to a Table/View
--------------------------

LuxSQLTables can be connected to individual tables or views created within your Postgresql database. This can be done by either specifying the table/view name in the constructor.

.. code-block:: python

	sql_tbl = LuxSQLTable(table_name = "my_table")

You can also connect a LuxSQLTable to a table/view by using the set_SQL_table function.

.. code-block:: python

	sql_tbl = LuxSQLTable()
	sql_tbl.set_SQL_table("my_table")

Choosing an Executor
--------------------------

Once a user has created a connection to their Postgresql database, they need to change Lux's execution engine so that the system can collect and process the data properly.
By default Lux uses the Pandas executor to process local data in the LuxDataframe, but users will use the SQL executor when their LuxSQLTable is connected to a database.
Users can specify the executor that Lux will use via the set_executor_type function as follows:

.. code-block:: python

	lux_df.set_executor_type("SQL")

Once a LuxSQLTable has been connected to a Postgresql table and set to use the SQL Executor, users can take full advantage of Lux's visual exploration capabilities as-is. Users can set their intent to specify which variables they are most interested in and discover insightful visualizations from their database.

SQL Executor Limitations
--------------------------

While users can make full use of Lux's functionalities on data within a database table, they will not be able to use any of Pandas' Dataframe functions to manipulate the data in the LuxSQLTable object. Since the Lux SQL Executor delegates most data processing to the Postgresql database, it does not pull in the entire dataset into the Lux Dataframe. As such there is no actual data within the LuxSQLTable to manipulate, only the relevant metadata required to for Lux to manage its intent. Thus, if users are interested in manipulating or querying their data, this needs to be done through SQL or an alternative RDBMS interface.