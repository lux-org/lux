***********************************
Ordering Outputs
***********************************

By default, Lux is trying to maximize the `interestingness function <interestingness.html>`_.
However, in some cases, perhaps you would like to sort by a different feature or attribute.
Here are some default sorters available to use:

Supported Orderings
====================


1. `"interestingness"`: This is the default sorter selected in Lux. It scores by the `interestingness function <interestingness.html>`_.

2. `"alphabetical_by_title"`: This sorter allows for alphabetical sorting based on the title.

3. `"alphabetical_by_x"` : This sorter allows for alphabetical sorting based on the attribute featured on the x-axis.

4. `"alphabetical_by_y"` : This sorter allows for alphabetical sorting based on the attribute featured on the y-axis.

Custom Orderings
====================

You can also add a custom sorter by creating a function that takes in a collection and a direction (ascending or descending)
and returns the sorted collection.

For example,

.. code-block:: python

    def sort_by_multiple(collection, desc):
        collection.sort(key=lambda x: (x.get_attr_by_channel("x")[0].attribute, x.get_attr_by_channel("y")[0].attribute), reverse=False)
    lux.config.ordering = sort_by_multiple

In this example, instead of sorting by just the x attribute or y attribute, we'd like to sort first by the x attribute and then sort by the y attribute.
The last line sets this to the globally defined ordering, which means that all actions will be ordered using this function.

Action-Dependent Orderings
==========================
There are some cases where we'd like to sort the outputs of different actions differently.
To do so, you can add to the :code:`lux.config.ordering_actions` dictionary. To set an action's ordering,
you can do the following, for example:

.. code-block:: python

    lux.config.ordering_actions["correlation"] = "alphabetical_by_x"

To remove the ordering for the action, simply reset the dictionary's entry to an empty string, like so:

.. code-block:: python

    lux.config.ordering_actions["correlation"] = ""

Changing the sorting direction
==============================

By default, Lux is trying to `maximize` an objective function, whether that be `interestingness` or some other custom function you define.
Thus, the default sorting direction is :code:`"descending"`. In order to toggle it, you can use:

.. code-block:: python

    lux.config.sort = "ascending" # or "descending" or "None" for no sorting order

This is a globally defined sort order.



