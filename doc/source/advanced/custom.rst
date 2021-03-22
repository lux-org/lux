***********************************
Registering Custom Recommendations
***********************************

.. note:: You can follow along this tutorial in a Jupyter notebook. [`Github <https://github.com/lux-org/lux-binder/blob/master/tutorial/8-custom-action.ipynb>`_] [`Binder <https://mybinder.org/v2/gh/lux-org/lux-binder/master?urlpath=tree/tutorial/8-custom-action.ipynb>`_]

In this tutorial, we will look at how you can register custom recommendation actions (i.e. tabs of recommendations) to display on the Lux widget. The custom actions can be globally defined and used across different dataframes. We look at the `Happy Planet Index <http://happyplanetindex.org/>`_ dataset, which contains metrics related to well-being for 140 countries around the world. 

.. code-block:: python

    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/hpi.csv")
    df["G10"]  = df["Country"].isin(["Belgium","Canada","France","Germany","Italy","Japan","Netherlands","United Kingdom","Switzerland","Sweden","United States"])
    lux.config.default_display = "lux"

As we can see, Lux registers a set of default recommendations to display to users, such as Correlation, Distribution, etc.

.. code-block:: python

    df

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/custom-3.png?raw=true
    :width: 700
    :align: center
    :alt: Displays default actions after print df.

Registering Custom Actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's define a custom function to generate the recommendations on the dataframe. In this example, we register a custom action that showcases numerical measures that differs significantly across G10 and non-G10 countries. `G10 countries<https://en.wikipedia.org/wiki/Group_of_Ten_(economics)>` are composed of the ten most industrialized countries in the world, so comparing G10 and non-G10 countries allows us to understand how industrialized and non-industrialized economies differs based on the measures present in the dataframe. 

Here, we first generate a VisList that looks at how various quantitative attributes breakdown between G10 and non-G10 countries. Then, we score and rank these visualization by calculating the percentage difference in means across G10 v.s. non-G10 countries.

.. code-block:: python

    from lux.vis.VisList import VisList
    # Create a VisList containing G10 with respect to all possible quantitative columns in the dataframe
    intent = [lux.Clause("?",data_type="quantitative"),lux.Clause("G10")]
    vlist = VisList(intent,df)
    
    for vis in vlist:
        # Percentage Change Between G10 v.s. non-G10 countries
        a = vis.data.iloc[0,1]
        b = vis.data.iloc[1,1]
        vis.score = (b-a)/a
    vlist.sort()
    vlist.showK()

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/custom-0.png?raw=true
    :width: 700
    :align: center
    :alt: Custom VisList of G10 v.s. non G10 countries

To define a custom action, we simply wrap our earlier VisList example into a function. We can even use short texts and emojis as the title to display on the tabs for the custom recommendation.

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
        vlist.sort()
        vlist.showK()
        return {"action":"Compare 🏭🏦🌎", 
                "description": "Percentage Change of Means Between G10 v.s. non-G10 countries",
                "collection": vlist}

In the code below, we define a display condition function to determine whether or not we want to generate recommendations for the custom action. In this example, we simply check if we are using the HPI dataset to generate recommendations for the `Compare industrialized` action.

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

To register the `Compare industrialized` action in Lux, we apply the :code:`register_action` function, which takes a name and action as inputs, as well as a display condition and additional arguments as optional parameters.

.. code-block:: python
    
    lux.config.register_action("Compare industrialized", G10_mean_difference, is_G10_hpi_dataset)

After registering the action, the custom action is automatically generated when we display the Lux dataframe again.

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

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/custom-1-filtered.png?raw=true
  :width: 700
  :align: center
  :alt: Displays countries with GDPPerCapita > 40000 to compare G10 results.
  
As we can see, there is a less of a distinction between G10 and non-G10 countries across the measures when we only filter to only high GDP countries.

Navigating the Action Manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can inspect a list of actions that are currently registered in Lux's Action Manager. The following code displays both default and user-defined actions.

.. code-block:: python
    
    lux.config.actions

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/custom-5.png?raw=true
    :width: 700
    :align: center
    :alt: Retrieves a list of actions from Lux's action manager.

You can also get a single action attribute by calling this function with the action's name.

.. code-block:: python

    lux.config.actions.get("Compare industrialized")

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/custom-2.png?raw=true
  :width: 700
  :align: center
  :alt: Retrieves a single attribute from Lux's action manager using its defined id.

Removing Custom Actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's say that we are no longer interested in looking at the `Compare industrialized` action, the `remove_action` function allows you to remove from Lux's action manager an action with its id. The action will no longer display with the Lux dataframe.

.. code-block:: python
    
    lux.config.remove_action("Compare industrialized")

After removing the action, when we print the dataframe again, the `Compare industrialized` action is no longer displayed.


.. code-block:: python

    df

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/custom-3.png?raw=true
  :width: 700
  :align: center
  :alt: Demonstrates removing custom action from Lux Action Manager.