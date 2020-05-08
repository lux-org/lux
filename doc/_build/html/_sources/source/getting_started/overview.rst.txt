********
Overview
********

This tutorial provides an overview of how you can use Lux in your data exploration workflow. 
You can follow along the tutorial using this Jupyter notebook.

Lux Overview
---------------------

Lux is designed to be tightly integrated with `Pandas <https://pandas.pydata.org/>`_, so that Lux can be used as-is, without modifying your existing Pandas code.

.. code-block:: python

    import pandas as pd
    import lux

We can load the dataset via any of the standard Pandas commands. For example, 

.. code-block:: python

    df = pd.read_csv("lux/data/college.csv")
