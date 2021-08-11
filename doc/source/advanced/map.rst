************************************
Working with Geographic Data Columns
************************************

This tutorial describes how geographic attributes can be visualized automatically with Lux. 
Lux recognizes any columns named :code:`state` and :code:`country` that contains US States or worldwide countries as geographic attributes.
Geographic attributes are automatically plotted against other attributes in the dataset as `choropleths maps <https://en.wikipedia.org/wiki/Choropleth_map.html>`_ in Lux. 


Map of US States
--------------------------------------

Below we look at an example COVID-19 dataset that has a :code:`state` column, with each row representing data for a state in the US. 

.. code-block:: python
  
  df = pd.read_csv("https://github.com/covidvis/covid19-vis/blob/master/data/interventionFootprintByState.csv?raw=True",index_col=0)
  df

Under the :code:`Geographical` tab on the Lux widget, we immediately see a list of choropleths map demonstrating how different attributes vary by state.

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/map-1.png?raw=true
  :width: 600
  :align: center
  :alt: Geographic tab of COVID-19 dataset

:code:`state` is a special keyword that allows Lux to identify columns containing US states. If your dataframe contains a column with state information and the geographical visualization is not being displayed, you may have to rename the column as :code:`state`. 

Lux uses the `python-us package <https://github.com/unitedstates/python-us/blob/master/us/states.py>`_ to define the naming conventions for US states.
The :code:`state` column can either contain the full state name (e.g. "California"), abbreviation (e.g. "CA"), or FIPS code (e.g. 06) as values.

Map of World Countries
--------------------------

Below we look at the `Happy Planet Index (HPI) <http://happyplanetindex.org/>`_ dataset that has a :code:`country` column with each row representing data for a country in the world.

.. code-block:: python

  df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/hpi.csv")
  df

Under the "Geographical" tab on the Lux widget, we immediately see a list of choropleths maps demonstrating how attributes vary by country.

.. image:: https://github.com/lux-org/lux-resources/blob/master/doc_img/map-2.png?raw=true
  :width: 600
  :align: center
  :alt: Geographic tab of HPI dataset

:code:`country` is a special keyword that allows Lux to identify columns containing world countries. If your dataframe contains a column with country information and the geographical visualization is not being displayed, you may have to rename the column as :code:`country`. 

Lux uses the `iso3166 package <https://github.com/deactivated/python-iso3166/blob/master/iso3166/__init__.py>`_ to define the naming conventions for world countries.
The :code:`country` column can either contain full country name (e.g. "Afghanistan"), abbreviations (e.g. "AF" or "AFG"), or ISO code (e.g. 004) as values.