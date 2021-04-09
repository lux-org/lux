****************
Execution Engine
****************

Lux provides an extensible framework for users to pick their own execution backend for data processing. We currently support Pandas (default, :mod:`lux.executor.PandasExecutor`) and Postgresql (:mod:`lux.executor.SQLExecutor`). In this tutorial, we explain how to use Lux, a data exploration and visualization python library, with SQL databases using Lux’s SQL executor

Please refer to :mod:`lux.executor.Executor`, if you are interested in extending Lux for your own execution backend.



SQL Executor
=============

Lux extends its visualization exploration operations to data within SQL databases. By using the SQL Executor, users can specify a SQL database to connect a LuxSQLTable for generating all the visualizations recommended in Lux.


What is the SQL Executor
=============

Lux uses an execution engine to collect and process data from databases. By default, Lux’s executor engine is set for Pandas and works on Pandas Dataframes. However, if you store data on a Postgres SQL database, Lux can use the SQL executor to explore and visualize your SQL tables using its visualization recommendation system.       


Why use the LuxSQLTable
=============

As datasets grow larger, more and more people use databases for their data storage needs. However, fetching the data required for generating visualizations can be computationally expensive, especially on large database tables. Furthermore, individuals working with the data may not be able to pull in the entire dataset, either due to a lack of permissions or due to the data being too large to work with on a local machine. Thus in order to leverage Lux’ smart visual exploration system, you can use the LuxSQLTable and the Postgresql executor backend.

Terms to familiarize yourself: 
=============
1. LuxSQLTable: For generating all the visualizations and recommendations Lux creates a proxy for your SQL table with the LuxSQLTable object. If you’ve used Lux in the pandas environment, the LuxSQLTable is the database compatible version of the LuxDataFrame. It is important to note that you cannot use the usual Pandas Dataframe functions on the LuxSQLTable object. 

Before running Lux with SQL Executor:   
Make sure you’ve have following:
Jupyter notebook.
Postgresql database that you want to explore. 

Connecting Lux to a Database
----------------------------

Before Lux can operate on data within a Postgresql database, users have to connect their LuxSQLTable to their database.
To do this, users first need to specify a connection to their SQL database. This can be done using the psycopg2 package's functionality.

.. code-block:: python

	import psycopg2
	connection = psycopg2.connect("dbname=postgres_db_name user=example_user password=example_user_password")

Once this connection is created, users can connect the lux config to the database using the set_SQL_connection command.

.. code-block:: python

	lux.config.set_SQL_connection(connection)

When the set_SQL_connection function is called, Lux gets the details it needs to be able to connect to your PostgreSQL database and run the visualization recommendation system. 

Connecting a LuxSQLTable to a Table/View
--------------------------

LuxSQLTables can be connected to individual tables or views created within your Postgresql database. This can be done by either specifying the table/view name in the constructor. We are actively working on supporting joins between multiple tables. But as of now, the functionality is limited to one table/view per LuxSQLTable object only.

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

While users can make full use of Lux's functionalities on data within a database table, they will not be able to use any of Pandas' Dataframe functions to manipulate the data in the LuxSQLTable object. Since the Lux SQL Executor delegates most data processing to the Postgresql database, it does not pull in the entire dataset into the Lux Dataframe. As such there is no actual data within the LuxSQLTable to manipulate, only the relevant metadata required for Lux to manage its intent. Thus, if users are interested in manipulating or querying their data, this needs to be done through SQL or an alternative RDBMS interface.
At the moment, the Lux SQL executor also does not support JOIN operation on SQL tables. Therefore, you cannot explore data and create recommended visualizations across multiple SQL tables only through Lux. However, we are consistently working on expanding the SQL capabilities of Lux, so keep an eye on future updates! 
