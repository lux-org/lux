********************************
Defining Custom Actions Globally 
********************************

.. note:: You can follow along this tutorial in a Jupyter notebook. [`Github <https://github.com/lux-org/lux-binder/blob/master/tutorial/8-custom-action.ipynb>`_] [`Binder <https://mybinder.org/v2/gh/lux-org/lux-binder/master?urlpath=tree/tutorial/3-widget-vis-export.ipynb>`_]

In this tutorial, we look at the `Happy Planet Index <http://happyplanetindex.org/>`_ dataset, which contains metrics related to well-being for 140 countries around the world. We demonstrate how you can globally define custom actions on the lux API and share them across dataframes. 

.. code-block:: python

    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/hpi.csv")
    lux.config.default_display = "lux" # Set Lux as default display
    df

The dataframe initially registers a few default recommendations, such as Correlation, Enhance, Filter, etc.

Registering Custom Actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's define a custom function to generate the recommendations on the dataframe. In this example, we will use G10 to generate a VisList to calculate the percentage change of means Between G10 v.s. non-G10 countries.

.. code-block:: python

    def G10_mean_difference(ldf):
      intent = [lux.Clause("?",data_type="quantitative"),lux.Clause("G10")]
      vlist = VisList(intent,df)

      for vis in vlist:
          a = vis.data.iloc[0,1]
          b = vis.data.iloc[1,1]
          vis.score = (b-a)/a
      vlist = vlist.topK(15)
      return {"action":"G10", "description": "Percentage Change of Means Between G10 v.s. non-G10 countries", "collection": vlist}

In this block, we define a display condition function to determine whether or not we want to generate recommendations for the custom action. In this example, we simply check if we are using the HPI dataset to generate recommendations for G10.

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

Here, you can register the provided action globally in lux. The function register_action requires an id, action, (optional) display_condition and (optional) additional args for the action as parameters.

.. code-block:: python
    
    lux.register_action("G10", G10_mean_difference, is_G10_hpi_dataset)

We can generate the new custom recomendations by calling the Lux dataframe again.

.. code-block:: python

    df

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/custom-1.png?raw=true
  :width: 700
  :align: center
  :alt: Displays default and user-defined actions as a VisList.

Using our new action, we can modify our display to only show countries with that reach a certain threshold of GDP and see how their G10 difference compares. 

.. code-block:: python

    df[df["GDPPerCapita"]>40000]

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/custom-1.png?raw=true
  :width: 700
  :align: center
  :alt: Displays countries with GDPPerCapita > 40000 to compare G10 results.

Navigating the Action Manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To see what actions are defined on the Lux Action Manager, the following lines allow you to navigate lux.actions to see both default and user-defined actions.

.. code-block:: python
    
    lux.actions.__len__()
    lux.actions.__getactions__()

You can also get a single action attribute by calling this function with the action's id.

.. code-block:: python

    lux.actions.__getattr__("G10")

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/custom-2.png?raw=true
  :width: 700
  :align: center
  :alt: Retrieves a single attribute from Lux's Action Manager using its defined id.

Removing Custom Actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This simple function allows you to remove from Lux's action manager an action with its id. The action will no longer display with the Lux dataframe.

.. code-block:: python
    
    lux.remove_action("G10")
    df

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/custom-4.png?raw=true
  :width: 700
  :align: center
  :alt: Demonstrates removing custom action from Lux Action Manager.



