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
- How do I turn off Lux?
    - df.toPandas()
    - Remove `import lux` statement and restart Jupyter notebook.
- I want to change the opacity of my chart, add title, change chart font size, etc. How do I modify chart settings?
    - 
    - We currently only support chart modifications in Altair.

Troubleshooting Tips
-------------------

- The Jupyter widget does not show up when I print a dataframe.
    - Output message "A Jupyter widget could not be displayed because the widget state could not be found. This could happen if the kernel storing the widget is no longer available, or if the widget state was not saved in the notebook. You may be able to create the widget by running the appropriate cells."
    - Output message "LuxWidget(...)"
- When I print out the dataframe, the cell is taking a long time to run.
- I have a question or bug that is not addressed by any of the FAQs.