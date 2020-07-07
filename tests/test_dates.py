from .context import lux
import pytest
import pandas as pd
import numpy as np
from lux.utils import date_utils
from lux.executor.PandasExecutor import PandasExecutor

def test_dateformatter():
    ldf = pd.read_csv("lux/data/car.csv")
    ldf["Year"] = pd.to_datetime(ldf["Year"], format='%Y')  # change pandas dtype for the column "Year" to datetype
    timestamp = np.datetime64('2019-08-26')

    assert(date_utils.dateFormatter(timestamp,ldf) == '2019')

    ldf["Year"][0] = np.datetime64('1970-03-01') # make month non unique

    assert (date_utils.dateFormatter(timestamp, ldf) == '2019-8')


    ldf["Year"][0] = np.datetime64('1970-03-03') # make day non unique

    assert (date_utils.dateFormatter(timestamp, ldf) == '2019-8-26')

def test_period_selection():
	ldf = pd.read_csv("lux/data/car.csv")
	ldf["Year"] = pd.to_datetime(ldf["Year"], format='%Y')

	ldf["Year"] = pd.DatetimeIndex(ldf["Year"]).to_period(freq='A')

	ldf.setContext([lux.Spec(attribute = ["Horsepower","Weight","Acceleration"]),lux.Spec(attribute = "Year")])

	PandasExecutor.execute(ldf.view_collection,ldf)

	assert all([type(vc.data)==lux.luxDataFrame.LuxDataframe.LuxDataFrame for vc in ldf.view_collection])
	assert all(ldf.view_collection[2].data.columns ==["Year",'Acceleration'])

def test_period_filter():
	ldf = pd.read_csv("lux/data/car.csv")
	ldf["Year"] = pd.to_datetime(ldf["Year"], format='%Y')

	ldf["Year"] = pd.DatetimeIndex(ldf["Year"]).to_period(freq='A')

	ldf.setContext([lux.Spec(attribute = "Acceleration"),lux.Spec(attribute = "Horsepower")])

	PandasExecutor.execute(ldf.view_collection,ldf)
	ldf.show_more()

	assert isinstance(ldf.recommendation['Filter'][2].spec_lst[2].value, pd.Period)

def test_period_toAltair():
	chart = None
	df = pd.read_csv("lux/data/car.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y')

	df["Year"] = pd.DatetimeIndex(df["Year"]).to_period(freq='A')

	df.setContext([lux.Spec(attribute = "Acceleration"),lux.Spec(attribute = "Horsepower")])

	PandasExecutor.execute(df.view_collection,df)
	df.show_more()

	exportedCode = df.recommendation['Filter'][2].toAltair()
	
	assert 'Year = 1971' in exportedCode

def test_refresh_inplace():
	df = pd.DataFrame({'date': ['2020-01-01', '2020-02-01', '2020-03-01', '2020-04-01'], 'value': [10.5,15.2,20.3,25.2]})
	
	assert df.data_type['nominal'][0] == 'date'

	from lux.view.View import View
	view = View(["date","value"])
	view.load(df)

	df['date'] = pd.to_datetime(df['date'],format="%Y-%m-%d")

	assert df.data_type['temporal'][0] == 'date'
