********
Overview
********

This tutorial provides an overview of how you can use Lux in your data exploration workflow. 
You can follow along the tutorial using this Jupyter notebook. 

Note: This tutorial assumes that you have already installed Lux and the associate Jupyter widget, if you have not done so already, please check out this page.

.. TODO: add link to page

Lux Overview
---------------------

Lux is designed to be tightly integrated with `Pandas <https://pandas.pydata.org/>`_, so that Lux can be used as-is, without modifying your existing Pandas code.
Lux preserves the Pandas dataframe semantics -- which means that you can apply any command from Pandas's API to the dataframes in Lux and expect the same behavior.

.. code-block:: python

    import pandas as pd
    import lux

We can load the dataset via any of the standard Pandas commands. For example, 

.. code-block:: python

    df = pd.read_csv("lux/data/college.csv")

Lux is built on the philosophy that generating useful visualizations should be as simple as printing out a dataframe. 
When you print out the dataframe in the notebook, you see the default Pandas table with an additional button that allow you to explore the data visually through Lux.

.. TODO: insert image

When you click on this button, you should see three tabs of visualizations recommended to you. Next, we will describe the details of how these recommendations are generated.

.. TODO: insert image

Recommendations in Lux
---------------------


- describe Correlation, Distribution, Category
- example of how setContext changes the recommendations
- refer to rec details page
