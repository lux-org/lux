********************************
Frequently Asked Questions (FAQ)
********************************

General Information
-------------------
- How do I load in data for Lux? 
- What do I do if I want to change the data type of an attribute?
- How do I save my widgets in the notebook file?
- What do I do with date-related attributes in my dataset?
- What if my data is stored in a relational database?
- How do I access all of the current recommendations shown in my widget?

  - df.recommendation
- How do I set the Lux widgets to show up on default? 
    - By default, we show the Pandas display and users can use the toggle button to switch to the Lux display. The `set_default_display` function allows users to change the setting so that the Lux widget is set as the default view for future operations on the specified dataframe: 

    .. code-block:: python
    
        df.set_default_display("lux")
    
    To switch back to Pandas as the default display: 

    .. code-block:: python
    
        df.set_default_display("pandas")

- How do I turn off Lux?
    - To tempora
  - df.to_pandas()
  - Remove `import lux` statement and restart Jupyter notebook.
- I want to change the opacity of my chart, add title, change chart font size, etc. How do I modify chart settings?

  - We currently only support chart modifications in Altair.

- How do I override the default values in the Clause? For example, how do I change the aggregation function to be something that is not average? how do I set an attribute to display on the x-axis instead of y-axis? 
  - To override automatically inferred properties, you can specify additional arguements inside `lux.Clause` to set the value of the Clause properties. See the tutorial on `"Adding constraints" <https://lux-api.readthedocs.io/en/latest/source/guide/intent.html#adding-constraints>`_.

Troubleshooting Tips
-------------------

- The Lux Jupyter widget does not show up when I print a dataframe.
    - Output message "A Jupyter widget could not be displayed because the widget state could not be found. This could happen if the kernel storing the widget is no longer available, or if the widget state was not saved in the notebook. You may be able to create the widget by running the appropriate cells."
    - Output message "LuxWidget(...)"

- I'm not able to export my visualizations via `.get_exported()`
    - First, make sure that after selecting the visualization, you have clicked on the export button (attach screenshot)
    - If you are recieving a warning message "No widget attached to the dataframe/VisList. Please assign dataframe/VisList to an output variable." This means that the output widget that you exported your visualization on have not been stored to the variable that you are calling `get_exported` on. For example, you might have interacted with a widget directly by printing the results out.
    .. code-block:: python

       df.groupby("HighestDegree").sum().reset_index()

    You can resolve this issue by reassigning the dataframe or VisList output to a variable name, then exporting the visualization again based on the new widget.

    .. code-block:: python
    
        myOutput = df.groupby("HighestDegree").sum().reset_index()
        myOutput

    Then you should be able to access the exported visualizations by: 

    .. code-block:: python

        myOutput.get_exported()

- When I print out the dataframe, the cell is taking a long time to run.
- I have a question or bug that is not addressed by any of the FAQs.
    - Please submit a Github Issue or ask a question on Slack.