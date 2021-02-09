***********************************
Registering Custom Recommendations
***********************************

.. note:: You can follow along this tutorial in a Jupyter notebook. [`Github <https://github.com/lux-org/lux-binder/blob/master/tutorial/8-custom-action.ipynb>`_] [`Binder <https://mybinder.org/v2/gh/lux-org/lux-binder/master?urlpath=tree/tutorial/8-custom-action.ipynb>`_]

In this tutorial, we will look at how you can register custom recommendation actions (i.e. tabs of recommendations) to display on the Lux widget. The custom actions can be globally defined and used across different dataframes. We look at the `Happy Planet Index <http://happyplanetindex.org/>`_ dataset, which contains metrics related to well-being for 140 countries around the world. 

.. code-block:: python

    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/hpi.csv")
    df["G10"]  = df["Country"].isin(["Belgium","Canada","France","Germany","Italy","Japan","Netherlands","United Kingdom","Switzerland","Sweden","United States"])
    lux.config.default_display = "lux"
    df

As we can see, Lux displays several recommendation actions, such as Correlation and Distributions, which is globally registered by default.

Registering Custom Actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's define a custom function to generate the recommendations on the dataframe. In this example, we register a custom action called `G10` to generate a collection of visualizations that showcases numerical measures that differs significantly across `G10 <https://en.wikipedia.org/wiki/Group_of_Ten_(economics)>`_ and non-G10 countries. In other words, we want to understand how the G10 and non-G10 countries differs based on the measures present in the dataframe. 

Here, we first generate a VisList that looks at how various quantitative attributes breakdown between G10 and non-G10 countries. Then, we score and rank these visualization by calculating the percentage difference in means across G10 v.s. non-G10 countries.

.. code-block:: python

    from lux.vis.VisList import VisList
    intent = [lux.Clause("?",data_type="quantitative"),lux.Clause("G10")]
    vlist = VisList(intent,df)

    for vis in vlist:
        # Percentage Change Between G10 v.s. non-G10 countries 
        a = vis.data.iloc[0,1]
        b = vis.data.iloc[1,1]
        vis.score = (b-a)/a
    lux.config.topK = 15
    vlist = vlist.showK()

Let's define a custom function to generate the recommendations on the dataframe. In this example, we will use G10 to generate a VisList to calculate the percentage change of means Between G10 v.s. non-G10 countries.

.. code-block:: python

    def G10_mean_difference(ldf):
    # Define a VisList of quantitative distribution between G10 and non-G10 countries
        intent = [lux.Clause("?",data_type="quantitative"),lux.Clause("G10")]
        vlist = VisList(intent,ldf)

        # Score each Vis based on the how different G10 and non-G10 bars are
        for vis in vlist:
            a = vis.data.iloc[0,1]
            b = vis.data.iloc[1,1]
            vis.score = (b-a)/a
        lux.config.topK = 15
        vlist = vlist.showK()
        return {"action":"G10", "description": "Percentage Change of Means Between G10 v.s. non-G10 countries", "collection": vlist}

In the code below, we define a display condition function to determine whether or not we want to generate recommendations for the custom action. In this example, we simply check if we are using the HPI dataset to generate recommendations for the custom action `G10`.

.. code-block:: python

    def is_G10_hpi_dataset(df):
        try: 
            return all(df.columns == ['HPIRank', 'Country', 'SubRegion', 'AverageLifeExpectancy',
            'AverageWellBeing', 'HappyLifeYears', 'Footprint',
            'InequalityOfOutcomes', 'InequalityAdjustedLifeExpectancy',
            'InequalityAdjustedWellbeing', 'HappyPlanetIndex', 'GDPPerCapita',
            'Population', 'G10'])
        except: 
            return False

To register the `G10` action in Lux, we apply the `register_action` function, which takes a name and action as inputs, as well as a display condition and additional arguments as optional parameters.

.. code-block:: python
    
    lux.config.register_action("G10", G10_mean_difference, is_G10_hpi_dataset)

After registering the action, the G10 recomendation action is automatically generated when we display the Lux dataframe again.

.. code-block:: python

    df

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/custom-1.png?raw=true
  :width: 700
  :align: center
  :alt: Displays default and user-defined actions as a VisList.

As expected, we see that G10 and non-G10 countries differs significantly in terms of their GDPPerCapita, but also in terms of their carbon footprint (Footprint) and number of expected happy year an average citizen can expect to live within a country (HappyLifeYears).

Since the registered action is globally defined, the G10 action is displayed whenever the display condition is satisfied (i.e. if the data schema matches that of the HPI dataset). For example, we might want to isolate the GDPPerCapita factor and only examine countries with high GDP. We can filter to only countries with GDPPerCapita over 40k and see the difference across the various quantitative attributes for these countries. 

.. code-block:: python

    df[df["GDPPerCapita"]>40000]

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/custom-1.png?raw=true
  :width: 700
  :align: center
  :alt: Displays countries with GDPPerCapita > 40000 to compare G10 results.
  
As we can see, there is a less of a distinction between G10 and non-G10 countries across the measures when we only filter to only high GDP countries.

Navigating the Action Manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can inspect a list of actions that are currently registered in the Lux Action Manager. The following code displays both default and user-defined actions.

.. code-block:: python
    
    lux.config.actions

You can also get a single action attribute by calling this function with the action's name.

.. code-block:: python

    lux.config.actions.get("G10")

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/custom-2.png?raw=true
  :width: 700
  :align: center
  :alt: Retrieves a single attribute from Lux's action manager using its defined id.

Removing Custom Actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's say that we are no longer in looking at the `G10` action, the `remove_action` function allows you to remove from Lux's action manager an action with its id. The action will no longer display with the Lux dataframe.

.. code-block:: python
    
    lux.config.remove_action("G10")

After removing the action, when we print the dataframe again, the `G10` action is no longer displayed.

.. code-block:: python

    df

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/custom-4.png?raw=true
  :width: 700
  :align: center
  :alt: Demonstrates removing custom action from Lux Action Manager.