********************************
Frequently Asked Questions (FAQ)
********************************

General Information
-------------------

How do I load in data for Lux? 
""""""""""""""""""""""""""""""""""""""""""""""""""""""""
You can use any of the data loading or dataframe creation commands from Pandas to load in data to be used with Lux. 
Note that you must perform :code:`import lux` before you load in or create the dataframe.

What if my data is stored in a relational database?
""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  Lux has `some limited support <https://lux-api.readthedocs.io/en/latest/source/advanced/executor.html#sql-executor>`__ for SQL (currently only tested for Postgres). We are actively working on extending Lux to databases. If you are interested in using this feature, please `contact us <https://communityinviter.com/apps/lux-project/lux>`_ for more information.

What do I do with date-related attributes in my dataset?
""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  Lux supports a variety of temporal data types in Pandas. For more information on how to handle temporal data in Lux, refer to `the datetime guide <https://lux-api.readthedocs.io/en/latest/source/advanced/date.html>`__.

What do I do with geographical attributes in my dataset?
""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  Lux supports a variety of geographical data types in Pandas. For more information on how to handle temporal data in Lux, refer to `the geographic entity tutorial <https://lux-api.readthedocs.io/en/latest/source/advanced/map.html>`__.

How do I access all of the current recommendations shown in my widget?
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  The recommendations for Lux can be accessed via the :code:`recommendation` property of the dataframe (e.g., :code:`df.recommendation`).

How do I set the Lux widgets to show up on default? 
""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  By default, we show the Pandas display and users can use the toggle button to switch to the Lux display. The :code:`default_display` property allows users to change the setting so that the Lux widget is set as the default view for future operations: 

    .. code-block:: python
    
        lux.config.default_display = "lux"
    
  To switch back to Pandas as the default display: 

    .. code-block:: python
    
        lux.config.default_display = "pandas"

How do I change the plotting library used for visualization?
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  By default, we make use of `Altair <https://altair-viz.github.io/>`__ to generate `Vega-Lite <https://vega.github.io/vega-lite>`__ visualizations. We can modify the :code:`plotting_backend` config property to use `Matplotlib <https://matplotlib.org/>`__ as the plotting library instead: 

    .. code-block:: python
    
        lux.config.plotting_backend = "matplotlib"
    
  To switch back to Vega-Lite: 

    .. code-block:: python
    
        lux.config.plotting_backend = "vegalite"
  
I want to change the opacity of my chart, add title, change chart font size, etc. How do I modify chart settings?
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  To add custom plot settings to the recommendations, you can set the :code:`lux.config.plotting_style` property. See `this tutorial <https://lux-api.readthedocs.io/en/latest/source/guide/style.html>`__ on how to configure chart properties. Lux supports chart modifications in Altair and Matplotlib.

How do I change aggregation functions, binning, or axis channels to non-default values?
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  To change the aggregation function to be something that is not average or set an attribute to display on the x-axis instead of y-axis, you can override the default values in the :code:`lux.Clause` specification.
  To override automatically inferred properties, you can specify additional arguements inside :py:class:`lux.vis.Clause` to set the value of the Clause properties. See `this page <https://lux-api.readthedocs.io/en/latest/source/guide/intent.html#adding-constraints>`__ for more details.

I want to look at the default recommendations that were recommended to me, how can I get the dataframe to display those?
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  To avoid information overload, Lux only displays the most relevant visualization to the user's intent at that point. To get to the default recommendation (e.g., Correlation, Distribution, Occurrence, Temporal), you should first clear the intent attached to the dataframe

  .. code-block:: python

      df.clear_intent()

  Then you should see the visualizations after printing it out again.

  .. code-block:: python

      df

How do I turn off Lux?
""""""""""""""""""""""""""
  To display only the Pandas view of the dataframe, print the dataframe by doing :code:`df.to_pandas()`.
  To turn off Lux completely, remove the :code:`import lux` statement and restart your Jupyter notebook.

How do I disable sampling and have Lux visualize the full dataset?
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  When visualizing large datasets, Lux may display a warning stating "`Large dataframe detected: Lux is only visualizing a random sample`". If you would like to disable sampling, you can run: 

  .. code-block:: python

      lux.config.sampling = False

  Note that if you have already loaded your data in and printed the visualizations, you would need to reinitialize the Dataframe by setting the config before loading in your data, as such:

  .. code-block:: python

      lux.config.sampling = False
      df = pd.read_csv("...")

  If you want to fine-tune the sampling parameters, you can edit :code:`lux.config.sampling_start` and :code:`lux.config.sampling_cap`. See `this page <https://lux-api.readthedocs.io/en/latest/source/reference/config.html>`__ for more details.

Troubleshooting Tips
--------------------

To troubleshoot your Lux installation, we recommend cloning `this repo <https://github.com/lux-org/lux-binder>`__ and using one of the `demo notebooks <https://github.com/lux-org/lux-binder/blob/master/demo/cars_demo.ipynb>`__ to test out Lux.

The Lux Jupyter widget does not show up when I print a dataframe.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
To check if your luxwidget configuration is set up correctly, please run the following code in your notebook to debug:
  
  .. code-block:: bash
  
    import lux
    lux.debug_info()
  
  We recommend using a simple example to test if your widget is showing correctly:

  .. code-block:: bash
  
    import lux
    import pandas as pd
    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/college.csv")
    df

  If you receive the output message :code:`❌ IPython shell not available.`, please run your code in a notebook interface such as Jupyter notebook, Jupyter Lab, JupyterHub, or VSCode.
  
  If you receive the output message :code:`❌ WARNING: luxwidget is not enabled in Jupyter Lab.`, run the following code in your terminal to enable luxwidget:
  
  .. code-block:: bash
  
    jupyter labextension install @jupyter-widgets/jupyterlab-manager
    jupyter labextension install luxwidget
    
  If you receive the output message :code:`❌ WARNING: luxwidget is not enabled in Jupyter Notebook.`, run the following code in your terminal to enable luxwidget: 
  
  .. code-block:: bash
  
    jupyter nbextension install --py luxwidget
    jupyter nbextension enable --py luxwidget
   

If the Lux Jupyter widget still does not show up, try the following:

  - If you receive the output message :code:`LuxWidget(...)` but you do not see Lux widget show up, it is possible that the widget is not installed correctly. Run :code:`jupyter nbextension list` on the terminal, and you should see the following as one of the listed items. 
  
  .. code-block:: bash
  
    luxWidget/extension  enabled
        - Validating: OK

  - If you are able to import lux successfully and you do not see the "Toggle button" when you print the dataframe, it may be possible that Lux is not compatible with your browser. Lux is compatible with Google Chrome, but have not been extensively tested on Safari or Firefox.
  - If you recieve the error message :code:`A Jupyter widget could not be displayed because the widget state could not be found.` This could happen if the kernel storing the widget is no longer available, or if the widget state was not saved in the notebook. You may be able to create the widget by running the particular cell again. If this doesn't work, then you may want try restarting the notebook and rerun the cell.
  - If you receive the error message :code:`ModuleNotFoundError: No module named 'luxwidget'`, it is possible that your luxwidget and lux-api versions are not in sync. The latest version of lux-api requires luxwidget v0.1 or above. Try running the following code:
  .. code-block:: bash
  
    pip uninstall lux-api
    pip uninstall lux-widget
    pip uninstall jupyterlab_widgets 
    pip install lux-api
    
    jupyter labextension install @jupyter-widgets/jupyterlab-manager
    jupyter labextension install luxwidget

  - If you receive the error message :code:`PermissionError: [Errno 13] Permission denied.` during the execution of the command :code:`jupyter nbextension install --py luxwidget`, then you can add the flag :code:`--user` (:code:`jupyter nbextension enable --py --user luxwidget`).
  - Alternatively, if none of the above works. You can try creating a fresh virtual environment and follow the `quick install instructions <https://github.com/lux-org/lux#installation>`_.

  .. code-block:: bash

    pip uninstall lux-api
    pip uninstall lux-widget

    jupyter nbextension uninstall --py luxwidget
    jupyter nbextension disable --py luxwidget

    pip install lux-api

    jupyter nbextension install --py luxwidget
    jupyter nbextension enable --py luxwidget
  

I'm not able to export my visualizations via the :code:`exported` property.
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    - First, make sure that after selecting the visualization, you have clicked on the export button (attach screenshot)
    - If you are recieving a warning message "No widget attached to the dataframe/VisList. Please assign dataframe/VisList to an output variable." This means that the output widget that you exported your visualization on have not been stored to the variable that you are calling `get_exported` on. For example, you might have interacted with a widget directly by printing the results out.

    .. code-block:: python

       df.groupby("HighestDegree").sum()

    You can resolve this issue by reassigning the dataframe or VisList output to a variable name, then exporting the visualization again based on the new widget.

    .. code-block:: python
    
        myOutput = df.groupby("HighestDegree").sum()
        myOutput

    Then you should be able to access the exported visualizations by: 

    .. code-block:: python

        myOutput.exported

I have an issue that is not addressed by any of the FAQs.
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Please submit a `Github Issue <https://github.com/lux-org/lux/issues>`__ or ask a question on `Slack <https://communityinviter.com/apps/lux-project/lux>`__.

.. Not Currently Supported
.. - What do I do if I want to change the data type of an attribute?
.. - How do I save my widgets in the notebook file?
.. - When I print out the dataframe, the cell is taking a long time to run.
