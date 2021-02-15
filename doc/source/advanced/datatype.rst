***********************************
Defining Data Types
***********************************

.. note:: You can follow along this tutorial in a Jupyter notebook. 

.. contents:: :local:


Data Types
==========

Data types in Lux are used to generate suggested visualizations. 
These data types are automatically inferred based on the input `dataframe` which are then used by the
`Compiler <https://lux-api.readthedocs.io/en/latest/source/advanced/executor.html>`_ to fill in the missing information in each `Clause`. 
While `Clauses` are not always specified, the system infers intent based on user inputs as well as the structure of the `dataframe`.
These `Clauses` determine which visualizations will be displayed.

.. note:: For more information about how Lux creates visualizations from a `frame`, see `this page <https://lux-api.readthedocs.io/en/latest/source/advanced/architecture.html>`_.

Note that these data types are different from Pandas `dtype`. 


The following code snippet shows what data types were inferred:

.. code-block:: python

  df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/college.csv?raw=true")
  df.data_type

.. image:: https://github.com/jinimukh/lux-resources/blob/datatype/doc_img/datatype-4.png?raw=true
  :width: 300
  :align: center

Quantitative
------------
Quantitative data is used to describe numerical data. 
The is usually used when Lux detects that there is a count or measure of a certain attribute. 
In the example above, the column `AcceptanceRate` is quantitative because it is a measure. 
Also, any aggregate such as means and medians will be categorized as quantitative. 
Usually, Lux is able to compute Correlations between two quantitative columns and display them via scatterplots/heatmaps.

.. image:: https://github.com/jinimukh/lux-resources/blob/datatype/doc_img/datatype-1.png?raw=true
  :width: 700
  :align: center
  :alt: Displays correlation of quantitative variables.

Nominal
--------
Unordered, categorical attributes are detected as nominal data types. 
For example, `PredominantDegree` is nominal because rather than being an explicit measure, it describes an attribute. 
In this case, there are three possible values: `Associate`, `Bachelor's`, and `Certificate`.
Lux displays these variables under the `Occurrence` tab as bar charts for the number of occurrences. 
When two nominal variables are specified in an intent, a stacked bar chart is used to compare the two variables.


.. image:: https://github.com/jinimukh/lux-resources/blob/datatype/doc_img/datatype-2.png?raw=true
  :width: 700
  :align: center
  :alt: Displays bar chart for nominal variables.

Temporal
--------
The temporal data type is used when Lux thinks based on either the format of the data passed in or the title of the column that the data in that column is time-related.
Here is an example where temporal data is detected:

.. code-block:: python

    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/car.csv?raw=true")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df.intent=["Year"]
    df

.. note:: For more information on dates in Lux, see `this tutorial <https://lux-api.readthedocs.io/en/latest/source/advanced/date.html>`_.

Here, specifying intent as the temporal variable, the `Temporal` tab reflects a line graph of the records and time.

.. image:: https://github.com/jinimukh/lux-resources/blob/datatype/doc_img/datatype-3.png?raw=true
  :width: 700
  :align: center
  :alt: Displays line graph for temporal variables.

ID
---
The ID data type is chosen for any column that looks like an ID and shouldn't be plotted. For example, zip code, user ID, etc.
For example, in the code snipped below, we see that the column `enrolee_id` has numerical data, it is categorized as an `ID` data type, so no visualizations correspond to it.

.. code-block:: python

  df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/aug_test.csv?raw=true")
  df

.. image:: https://github.com/jinimukh/lux-resources/blob/datatype/doc_img/datatype-5.png?raw=true
  :width: 700
  :align: center

Changing the Inferred Data Type
================================
Lux attempts to infer the data type information for every column in the dataframe. However, sometimes there is ambiguity in how the data should be modelled, as a result, Lux can incorrectly label a column with wrong data type. For example:

.. code-block:: python

    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/communities.csv?raw=true")
    df.data_type

.. image:: https://github.com/jinimukh/lux-resources/blob/datatype/doc_img/datatype-6.png?raw=true
  :width: 300
  :align: center


Lux incorrectly assumes that `state` is an `quantitative` column because the column seems to be made of numbers. 
However, in reality, the column contains numbers which map to states.
Thus, this is probably better suited as a `nominal` column. 
To change the inferred data type, use the method below: 

.. code-block:: python

    df.set_data_type({"state":"nominal"})

Lux will now interpret the `state` column as a `nominal` variable. 
To make sure, we can always check using `df.data_type` which outputs the following results

.. image:: https://github.com/jinimukh/lux-resources/blob/datatype/doc_img/datatype-7.png?raw=true
  :width: 300
  :align: center

Now, the `state` column behaves like a `nominal` column as shown below:

.. image:: https://github.com/jinimukh/lux-resources/blob/datatype/doc_img/datatype-8.png?raw=true
  :width: 700
  :align: center