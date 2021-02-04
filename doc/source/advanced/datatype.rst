***********************************
Data Types in Lux
***********************************

.. note:: You can follow along this tutorial in a Jupyter notebook. 

Currently, Lux supports four data types:

* Quantitative
* Temporal
* Nominal
* ID

Note that these data types are different from Pandas `dtype`. These data types are automatically inferred based on the input `dataframe`.
The following code snippet shows what data types were inferred:

.. code-block:: python

  df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/college.csv?raw=true")
  df.data_type


Quantitative
------------
The quantitative data type is used when there is a count or measure of a certain attribute. 
In the example above, the column `AcceptanceRate` is quantitative because it is a measure. 
Also, any aggregate such as means and medians will be categorized as quantitative. 
Usually, Lux is able to compute Correlations between two quantitative columns or show the distribution of each column.

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
Upon more granular searches by specifying intent, stacked bar charts comparing two nominal variables is also possible.

.. image:: https://github.com/jinimukh/lux-resources/blob/datatype/doc_img/datatype-2.png?raw=true
  :width: 700
  :align: center
  :alt: Displays bar chart for nominal variables.

Temporal
--------
The temporal data type is used when Lux thinks based on either the format of the data passed in or the title of the column that the data in that column is time-sensitive.
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


Changing the Inferred Data Type
-------------------------------
Lux attempts to infer the data type information for every column in the dataframe. However, sometimes there is ambiguity in how the data should be modelled, as a result, Lux can incorrectly label a column with wrong data type. For example:

.. code-block:: python

    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/real_estate_tutorial.csv?raw=true")
    df


Lux incorrectly assumes that this is a temporal column because of the column name. However, in reality, the columns are an ordered months and years. Here is one way to fix the problem:

.. code-block:: python

    df.set_data_type({"Year": "nominal", "Month": "nominal"})

Now, the `Month` and `Year` columns behave like the nominal columns shown above.