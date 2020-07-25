********************************
Exporting Vis From Widget
********************************

In this tutorial, we look at the `Happy Planet Index <http://happyplanetindex.org/>`_ dataset, which contains metrics related to well-being for 140 countries around the world. We demonstrate how you can select visualizations of interest and export them for further analysis. 

.. code-block:: python

    import pandas as pd
    import lux

.. code-block:: python

    df = pd.read_csv("lux/data/hpi.csv")
    # Set Lux as default vis
    df.set_default_display("lux") 
    df

Exporting one or more visualizations from recommendation widget
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can click on visualizations of interest and export them into a separate widget.

.. code-block:: python

    bookmarked_charts = df.get_exported()
    bookmarked_charts

From the dataframe recommendations, the visualization showing the relationship between `GDPPerCapita` and `Footprint` is very interesting. In particular, there is an outlier with extremely high ecological footprint as well as high GDP per capita. So we click on this visualization and click on the export button.

.. code-block:: python

    df

.. code-block:: python

    vis = df.get_exported()[0]
    vis

Setting Visualizations as Context
~~~~~~~~~~~~~~~~~~~~~~~~

Now that we have exported the vis, we can set the new intent of the dataframe to be the vis to get more recommendations related to this visualization.

.. code-block:: python

    df.set_intent_as_vis(vis)
    df

Exporting Visualizations as Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's say that we are now interested in the bar chart distribution of country `SubRegion`.

.. code-block:: python
    vis = df.recommendation["Category"][0]
    vis

To allow further edits of visualizations, visualizations can be exported to code in `Altair <https://altair-viz.github.io/>`_ or as `Vega-Lite <https://vega.github.io/vega-lite/>`_ specification.

.. code-block:: python

    print (vis.to_Altair())

You can also export this as Vega-Lite specification and vis/edit the specification on `Vega Editor <https://vega.github.io/editor>`_.

.. code-block:: python

    print (vis.to_VegaLite())

Accessing Widget State
~~~~~~~~~~~~~~~~~~~~~~

We can access the set of recommendations generated for the dataframes via the properties `recommendation`.

.. code-block:: python
    
    df.recommendation

The resulting output is a dictionary, keyed by the name of the recommendation category.

.. code-block:: python
    
    df.recommendation["Distribution"]

You can also access the vis represented by the current intent via the property `current_vis`.

.. code-block:: python

    df.current_vis