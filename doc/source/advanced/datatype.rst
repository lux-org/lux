***********************************
Understanding Data Types in Lux
***********************************

.. note:: You can follow along this tutorial in a Jupyter notebook. [`Github <https://github.com/lux-org/lux-binder/blob/master/tutorial/9-datatype.ipynb?>`_] [`Binder <https://mybinder.org/v2/gh/lux-org/lux-binder/master?urlpath=tree/tutorial/9-datatype.ipynb?raw=true>`_]

In Lux, data types convey the high-level, semantic roles for each attribute, such as whether it is temporal, nominal, or quantitative. The detected data type information are then used to infer the appropriate types of visualization to display for each attribute. Note that data types in Lux are different from the `dtype <https://pandas.pydata.org/pandas-docs/stable/user_guide/basics.html#basics-dtypes>`_ in Pandas, which involve atomic types such as string, integer, and float. Lux automatically infers the data type information for each column in the dataframe. The following code snippet shows what data types were inferred:

.. code-block:: python

  df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/college.csv?raw=true")
  df.data_type

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/datatype-4.png?raw=true
  :width: 300


Supported Data Types
====================

The following data types are supported in Lux: 

.. contents:: :local:

.. .. seealso::
.. Lux data types are automatically inferred based on the input `dataframe` which are then used by the
.. `Compiler <https://lux-api.readthedocs.io/en/latest/source/advanced/executor.html>`_ to fill in the missing information in each `Clause`. 
.. While `Clauses` are not always specified, the system infers intent based on user inputs as well as the structure of the `dataframe`.
.. These `Clauses` determine which visualizations will be displayed. For more information about how Lux creates visualizations from a dataframe, see `this page <https://lux-api.readthedocs.io/en/latest/source/advanced/architecture.html>`_.


Quantitative
------------
Quantitative data is used to describe numerical measures. 
This data type is typically assigned when Lux a numerical column consisting of floats or integers has large numbers of distinct values.
In the example above, the column :code:`AcceptanceRate` is detected as an quantitative attribute. 

By default, Lux displays the :code:`Correlation` action, displaying the relationship between two :code:`quantitative` columns as scatterplots or heatmaps.

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/datatype-9.png?raw=true
  :width: 700
  :align: center
  :alt: Displays correlation of quantitative variables.

Lux also shows the :code:`Distribution` action, displaying the distribution of each :code:`quantitative` attributes.

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/datatype-10.png?raw=true
  :width: 700
  :align: center
  :alt: Displays correlation of quantitative variables.

Nominal
--------
Nominal data types describes unordered, categorical attributes.
For example, the attribute :code:`PredominantDegree` is nominal because it contains only three distinct values: :code:`Associate`, :code:`Bachelor's`, and :code:`Certificate`.
Below: Lux displays the occurence counts of nominal variables under the :code:`Occurrence` action as bar charts. 

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/datatype-11.png?raw=true
  :width: 700
  :align: center
  :alt: Displays bar chart for nominal variables.

Geographic
-----------
Geographic data types describe location-based attributes, such as US states and world countries. 
Lux infers that an attribute is geographical if it's column name is :code:`state` or :code:`country` and if the data content contain state or country information. For example, the :code:`Country` column is detected as a geographic data type in this example:

.. code-block:: python

  df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/hpi.csv")
  df

Here, the :code:`Geographical` tab shows different choropleth maps of how different measures vary by country.

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/map-2.png?raw=true
  :width: 600
  :align: center
  :alt: Geographic tab of HPI dataset

.. note:: For more information on geographic attributes in Lux, see `this tutorial <https://lux-api.readthedocs.io/en/latest/source/advanced/map.html>`_.
  
  
Temporal
--------
Temporal data types describe time-related attributes, such as dates and timestamps. 
Lux infers that an attribute is temporal based on the data format, content, and name of the column. 
For example, the :code:`Year` attribute is detected as a temporal data type in this example:

.. code-block:: python

    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/car.csv?raw=true")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df

Here, the :code:`Temporal` tab reflects a line graph of the records and time.

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/datatype-12.png?raw=true
  :width: 700
  :align: center
  :alt: Displays line graph for temporal variables.

.. note:: For more information on dates in Lux, see `this tutorial <https://lux-api.readthedocs.io/en/latest/source/advanced/date.html>`_.

ID
---
ID data type describes identifier columns, such as zip code, product or user ID.
Typically, columns that are detected as ID data type do not contain a lot of useful information and should not be plotted. 
For example, in the code snipped below, we see that the column :code:`enrolee_id` has numerical data, it is categorized as an :code:`ID` data type, so no visualizations correspond to it.

.. code-block:: python

  df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/aug_test.csv?raw=true")
  df

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/datatype-5.png?raw=true
  :width: 700
  :align: center

Changing the Inferred Data Type
================================
Lux attempts to infer the data type information for every column in the dataframe. However, sometimes there is ambiguity in how the data should be modelled. For example, perhaps an attribute is detected as an ID field, but it is better visualized as a quantitative column. Alternatively, there may be a column that looks quantitative, but would be better modelled as a nominal. For example:

.. code-block:: python

    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/communities.csv?raw=true")
    df.data_type

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/datatype-6.png?raw=true
  :width: 300

Lux incorrectly assumes that :code:`state` is a :code:`quantitative` column because the column seems to be made of numbers. If we plot a visualization based on state, a histogram is displayed:

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/datatype-13.png?raw=true
  :width: 250

However, in reality, :code:`state` does not represent numbers with any meaningful relationship since the numbers discretely map to individual states. 
In this case, the :code:`state` column is better suited as a :code:`nominal` column. 
To change the inferred data type, use the :code:`set_data_type` method: 

.. code-block:: python

    df.set_data_type({"state":"nominal"})

The user specified data type information overrides the lux-detected data type.
From now on, Lux will interpret the :code:`state` column as :code:`nominal`. 
We can validate this by inspecting :code:`df.data_type`:

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/datatype-7.png?raw=true
  :width: 300

Now, when we plot the same visualization again, the :code:`nominal` :code:`state` column is displayed as a bar chart visualization. This bar chart visualization shows that state 6, 34, and 48 has the largest number of records, an insight that was hidden away in the binned histogram when the data type was misdetected.

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/datatype-14.png?raw=true
  :width: 250