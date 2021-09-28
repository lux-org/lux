***********************************
Custom Ranking across Actions
***********************************

In Lux, visualizations in each tab (i.e., action) are ordered based on a scoring function, by default, Lux ranks visualizations in descending order based on their `interestingness score <interestingness.html>`_ (i.e., showing the most interesting visualizations at the top of the list). In some cases, you may want to customize how the list of visualizations are ranked. Lux offers some additional ways to rank the visualizations across list of visualization in an action.

Here is the default set of keywords corresponding to different sorters supported in Lux:

- :code:`interestingness`: This is the default sorter selected in Lux, which scores each visualization based on its `interestingness function <interestingness.html>`_.

- :code:`alphabetical_by_title`: This sorter orders the visualizations  based on alphabetical sorting by the visualization's title.

- :code:`alphabetical_by_x`: This sorter orders the visualizations based on alphabetical sorting by the visualization's x-axis attribute.

- :code:`alphabetical_by_y`: This sorter orders the visualizations based on alphabetical sorting by the visualization's y-axis attribute.


Changing sorter for specified action
======================================
The sorting function is tied to each action, for example, the :code:`Correlation` action is sorted based on the correlation score as part of :code:`interestingness`.
To change the sorting function for specific actions, you can modify :code:`lux.config.ordering_actions`, which is a dictionary keyed by the action name, followed by the sorter name. For example, to change the :code:`Correlation` action to sort by alphabetical ordering based on the attribute on the x-axis.

.. code-block:: python

    lux.config.ordering_actions["correlation"] = "alphabetical_by_x"

To reset the action ranking based on its default, simply reset the entry with an empty string, as follows:

.. code-block:: python

    lux.config.ordering_actions["correlation"] = ""



Defining sorter based on custom function
==============================================

You can also add a custom sorter by creating a function that takes in a collection and a direction (ascending or descending)
and returns the sorted collection.
In following example, instead of sorting by just the x or y attribute, we'd like to sort first by the x attribute and then sort by the y attribute.
The last line sets this to the globally defined ordering, which means that all actions will be ordered using this function.


.. code-block:: python

    def sort_by_multiple(collection, desc):
        collection.sort(key=lambda vis: (vis.get_attr_by_channel("x")[0].attribute, vis.get_attr_by_channel("y")[0].attribute), reverse=False)
    lux.config.ordering = sort_by_multiple


Changing the sorting direction
==============================

By default, Lux tries to sort by maximizing the provided scoring function, so the default sorting direction is :code:`"descending"`. In order to change that, you can modify :code:`lux.config.sort`:

.. code-block:: python

    lux.config.sort = "ascending" # or "descending" or "None" for no sorting order

The sort order is defined globally and applied across all actions in Lux.
