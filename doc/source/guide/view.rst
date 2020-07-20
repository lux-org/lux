********************************
Specifying Vis/Vis Collections
********************************

:mod:`lux.vis.Vis` objects represents individual visualizations displayed in Lux. Lists of views are stored as :mod:`lux.vis.VisCollection` objects.
Views can either be automatically generated in Lux or defined by the user.

Basic descriptions 
------------------
We can create a visualization by defining a view. A view is simply a skeleton of the visualization. 

.. code-block:: python
    from lux.vis.Vis import Vis
    view = Vis(["MilesPerGal"])

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

.. to_Altair
.. to_VegaLite

.. `set_context_as_view`