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

.. code-block:: python

    df

.. TODO: insert image

When you click on this button, you should see three tabs of visualizations recommended to you. 

.. TODO: insert image

Voila! You have generated your first set of recommendations through Lux!
We will describe the details of how these recommendations are generated in the later portion of this tutorial.

.. TODO: insert link

Context: Specification of User Intent
-------------------------------------

We just saw an example of how recommendations can be generated for the dataset without providing additional information.
Beyond these overview visualizations, you can further specify the data attributes and values that you are interested in to Lux. 
This specification is known as the _context_.  
For example, let's say that you are interested in learning more about the median earning of students after they attend the college (i.e. the attribute `MedianEarning`).

.. code-block:: python

    df.setContext(["MedianEarnings"])

When you print out the dataframe again, you should see three tabs of visualizations recommended to you. 

.. code-block:: python

    df

.. TODO: insert image

Lux is built on the principle that users should always be able to visualize and explore anything they specify, without having to think about how the visualization should look like. 
Here, the Current View visualization represent the visualization that you have specified. 
On the right, you will again see the recommendations based on this Current View.

You can specify a variety of things that you might be interested in, for example, let's say that you are interested in the the median earnings of students in publicly-funded colleges.

.. code-block:: python

    df.setContext(["MedianEarnings", "FundingModel=Public"])

For more advance use of context, refer to this page on how to specify the context.

Recommendations in Lux
----------------------

Recommendations highlight interesting patterns and trends in the dataset.

Correlation 
- describe Correlation, Distribution, Category
- example of how setContext changes the recommendations
- refer to rec details page
