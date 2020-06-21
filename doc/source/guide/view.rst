********************************
Specifying View/View Collections
********************************

:mod:`lux.view.View` objects represents individual visualizations displayed in Lux. Lists of views are stored as :mod:`lux.view.ViewCollection` objects.
Views can either be automatically generated in Lux or defined by the user.

Basic descriptions 
------------------
We can create a visualization by defining a view. A view is simply a skeleton of the visualization. 

.. code-block:: python
    from lux.view.View import View
    view = View(["MilesPerGal"])

To render the visualization, we need to attach the view to data via the load function.
.. [Note: Alternatives to `load`]

.. code-block:: python
    view = view.load(df)

The decoupling of the view and its associated data is useful for making quick comparisons. 
.. For example 

.. Specifying attributes of interest
.. ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. Exported Views
.. --------------

.. toAltair
.. toVegaLite