********************************
Data Types in Lux
********************************

Currently, Lux supports 4 data types:

* Nominal
* Quantitative
* ID
* Temporal

Note that these Lux Data Types are different from `dtypes` in the Pandas DataFrame.

To find what the Lux Data Types are, use `df.data_type`. This returns a dictionary object mapping each attribute to a data type. For example,

.. code-block:: python

    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/car.csv?raw=true")
    df.data_type