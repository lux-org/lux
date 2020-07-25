********************************
Exporting Vis From Widget
********************************

In this tutorial, we look at the `Happy Planet Index <http://happyplanetindex.org/>`_ dataset, which contains metrics related to well-being for 140 countries around the world. We demonstrate how you can select visualizations of interest and export them for further analysis. 

.. code-block:: python

    import pandas as pd
    import lux

.. code-block:: python

    df = pd.read_csv("lux/data/hpi.csv")
    df.set_default_display("lux") # Set Lux as default display

Note that for the convienience of this tutorial, we have set Lux as the default display so we don't have to Toggle from the Pandas table display everytime we print the dataframe.

Exporting one or more visualizations from recommendation widget
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Lux, you can click on visualizations of interest and export them into a separate widget for further processing.

.. code-block:: python

    df

.. TODO add GIF 1) scroll through Correlation, then 2) click on any 3 visualization (let's say 2nd, 5th and something towards the end), then 3) click on the export button and make sure the blue message box show up 
.. TODO add this GIF to ipynb also.

.. code-block:: python

    bookmarked_charts = df.get_exported()
    bookmarked_charts

.. TODO add screenshot of exported VisList (include the Out[] __repr__ string) in screenshot

From the dataframe recommendations, the visualization showing the relationship between `GDPPerCapita` and `Footprint` is very interesting. In particular, there is an outlier with extremely high ecological footprint as well as high GDP per capita. So we click on this visualization and click on the export button.

.. code-block:: python

    df

.. TODO add GIF 1) scroll and find the vis for GDPPerCapita and Footprint 2) select and export this vis

.. code-block:: python

    vis = df.get_exported()[0]
    vis

.. TODO add screenshot of exported vis

Setting Visualizations as Context
~~~~~~~~~~~~~~~~~~~~~~~~

Now that we have exported the vis, we can set the new intent of the dataframe to be the vis to get more recommendations related to this visualization.

.. code-block:: python

    df.set_intent_as_vis(vis)
    df

.. TODO add screenshot

Accessing Widget State
~~~~~~~~~~~~~~~~~~~~~~

We can access the set of recommendations generated for the dataframes via the properties `recommendation`.

.. code-block:: python
    
    df.recommendation

.. TODO add screenshot

The resulting output is a dictionary, keyed by the name of the recommendation category.

.. code-block:: python
    
    df.recommendation["Enhance"]

.. TODO add screenshot

You can also access the vis represented by the current intent via the property `current_vis`.

.. code-block:: python

    df.current_vis

.. TODO add screenshot

Exporting Visualizations as Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's revist our earlier recommendations by clearing the specified intent.

.. code-block:: python

    df.clear_intent()
    df
.. TODO add GIF 1) click on `Category` tab, then 2) hover around the SubRegion v.s. Count of Records chart

Looking at the Category tab, we are interested in the bar chart distribution of country `SubRegion`.

.. code-block:: python
    vis = df.recommendation["Category"][0]
    vis

.. TODO add screenshot 

To allow further edits of visualizations, visualizations can be exported to code in `Altair <https://altair-viz.github.io/>`_ or as `Vega-Lite <https://vega.github.io/vega-lite/>`_ specification.

.. code-block:: python

    print (vis.to_Altair())

.. TODO add screenshot 

This can be copy-and-pasted back into a new notebook cell for further editing.

.. code-block:: python

    import altair as alt
    visData = pd.DataFrame({'SubRegion': {0: 'Americas', 1: 'Asia Pacific', 2: 'Europe', 3: 'Middle East and North Africa', 4: 'Post-communist', 5: 'Sub Saharan Africa'}, 'Record': {0: 25, 1: 21, 2: 20, 3: 14, 4: 26, 5: 34}})

    chart = alt.Chart(visData).mark_bar().encode(
        y = alt.Y('SubRegion', type= 'nominal', axis=alt.Axis(labelOverlap=True), sort ='-x'),
        x = alt.X('Record', type= 'quantitative', title='Count of Record'),
    )
    chart = chart.configure_mark(tooltip=alt.TooltipContent('encoding')) # Setting tooltip as non-null
    chart = chart.configure_title(fontWeight=500,fontSize=13,font='Helvetica Neue')
    chart = chart.configure_axis(titleFontWeight=500,titleFontSize=11,titleFont='Helvetica Neue',
                labelFontWeight=400,labelFontSize=8,labelFont='Helvetica Neue',labelColor='#505050')
    chart = chart.configure_legend(titleFontWeight=500,titleFontSize=10,titleFont='Helvetica Neue',
                labelFontWeight=400,labelFontSize=8,labelFont='Helvetica Neue')
    chart = chart.properties(width=160,height=150)
    chart

.. TODO add screenshot 

You can also export this as Vega-Lite specification and vis/edit the specification on `Vega Editor <https://vega.github.io/editor>`_.

.. code-block:: python

    print (vis.to_VegaLite())

.. TODO add screenshot of what this looks like in Vega Editor