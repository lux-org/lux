********************************
How To Use Config Class 
********************************

In this tutorial, we look at the functionality of the global Config class.

.. code-block:: python

    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/hpi.csv")
    df

The dataframe initially registers a few default recommendations, such as Correlation, Enhance, Filter, etc, and defaults to a pandas display.

Registering Custom Actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's set the default_display of the global class 'Config' to change the default form of output. In the following block, we set it to 'lux,' therefore the VisList will display first.

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

