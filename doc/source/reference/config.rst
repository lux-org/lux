***********************
Configuration Settings 
***********************

In Lux, users can customize various global settings to configure the behavior of Lux through :py:mod:`lux.config.Config`. This page documents some of the configurations that you can apply in Lux.


Change the default display of Lux
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can set the `default_display` of the global class 'Config' to change the default form of output. In the following block, we set it to 'lux,' therefore the VisList will display first.

.. code-block:: python

    lux.config.default_display = "lux" # Set Lux as default display
    df

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/display-1.png?raw=true
  :width: 700
  :align: center
  :alt: Retrieves a single attribute from Lux's Action Manager using its defined id.

We can set the default_display back to 'pandas,' which would allow for the dataframe object to display first. You can still toggle to Lux/Pandas respectively using the 'Toggle' button.

.. code-block:: python

    lux.config.default_display = "pandas" # Set Pandas as default display
    df

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/display-2.png?raw=true
  :width: 700
  :align: center
  :alt: Retrieves a single attribute from Lux's Action Manager using its defined id.

If you try to set the default_display to anything other than 'lux' or 'pandas,' a warning will be shown, and the display will default to the previous setting.

.. code-block:: python
    
    lux.config.default_display = "notpandas" # Throw an warning
    df

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/display-3.png?raw=true
  :width: 700
  :align: center
  :alt: Retrieves a single attribute from Lux's Action Manager using its defined id.

Change the sampling parameters of Lux
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To speed up the visualization processing, by default, Lux performs random sampling on datasets with more than 10000 rows. For datasets over 30000 rows, Lux will randomly sample 30000 rows from the dataset.

If we want to change these parameters, we can set the `sampling_start` and `sampling_cap` via `lux.config` to change the default form of output. The `sampling_start` is by default set to 10000 and the `sampling_cap` is by default set to 30000. In the following block, we increase these sampling bounds.

.. code-block:: python

    lux.config.sampling_start = 20000
    lux.config.sampling_cap = 40000

If we want Lux to use the full dataset in the visualization, we can also disable sampling altogether (but note that this may result in long processing times). Below is an example if disabling the sampling:

.. code-block:: python

    lux.config.sampling = False

Disable the use of heatmaps for large datasets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to sampling, Lux replaces scatter plots with heatmaps for datasets with over 5000 rows to speed up the visualization process.

We can disable this feature and revert back to using a scatter plot by running the following code block (but note that this may result in long processing times).

.. code-block:: python

    lux.config.heatmap = False
