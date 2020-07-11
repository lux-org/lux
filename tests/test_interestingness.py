from .context import lux
import pytest
import pandas as pd
import numpy as np
from lux.interestingness.interestingness import interestingness

# The following test cases are labelled for views with <Ndim, Nmsr, Nfilter>

#TODO: interestingness test needs to validate the characteristics of the resulting recommendation ranking, e.g. skewed histograms are ranked higher than uniform ones, etc.

def test_interestingness_1_0_0():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y')
    
    df.setContext([lux.Spec(attribute = "Origin")])
    df.executor.execute(df.viewCollection,df)
    #check for top recommended Enhance graph
    assert df.recommendation['Enhance'][0].mark == 'bar'
    assert df.recommendation['Enhance'][0].specLst[0].attribute == 'Displacement'
    assert df.recommendation['Enhance'][0].specLst[0].aggregation == 'mean'

    assert df.recommendation['Enhance'][0].specLst[1].attribute == 'Origin'
    assert df.recommendation['Enhance'][0].specLst[1].aggregation == ''

    #check that graph with filter 
    rank1 = -1
    rank2 = -1
    rank3 = -1
    for f in range(0, len(df.recommendation['Filter'])):
        if int(df.recommendation['Filter'][f].specLst[2].value) == 8:
            rank1 = f
        if int(df.recommendation['Filter'][f].specLst[2].value) == 6:
            rank2 = f
        if '1972' in str(df.recommendation['Filter'][f].specLst[2].value):
            rank3 = f
    assert rank1 < rank2 and rank1 < rank3 and rank2 < rank3

# def test_interestingness_1_0_1():
#     df = pd.read_csv("lux/data/car.csv")
#     df["Year"] = pd.to_datetime(df["Year"], format='%Y')
    
#     df.setContext([lux.Spec(attribute = "Origin", filterOp="=",value="USA"),lux.Spec(attribute = "Origin")])
#     assert df.viewCollection[0].mark == 'bar'
#     assert df.viewCollection[0].specLst[0].attribute == "Record"
#     assert df.viewCollection[0].specLst[0].aggregation == "count"
#     assert df.viewCollection[0].specLst[1].attribute == "Origin"


def test_interestingness_0_1_0():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y')

    df.setContext([lux.Spec(attribute = "Horsepower")])
    #check for top recommended Enhance graph
    assert df.recommendation['Enhance'][0].mark == 'scatter'
    assert df.recommendation['Enhance'][0].specLst[0].attribute == 'Horsepower'
    assert df.recommendation['Enhance'][0].specLst[1].attribute == 'Weight'

    #check that ordering of recommended filter graphs make sense
    rank1 = -1
    rank2 = -1
    rank3 = -1
    for f in range(0, len(df.recommendation['Filter'])):
        if df.recommendation['Filter'][f].specLst[2].value == 4:
            rank1 = f
        if str(df.recommendation['Filter'][f].specLst[2].value) == "Europe":
            rank2 = f
        if '1971' in str(df.recommendation['Filter'][f].specLst[2].value):
            rank3 = f
    assert rank1 < rank2 and rank1 < rank3 and rank2 < rank3


def test_interestingness_0_1_1():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y')
    
    df.setContext([lux.Spec(attribute = "Origin", filterOp="=",value="?"),lux.Spec(attribute = "MilesPerGal")])
    df
    assert np.isclose(interestingness(df.viewCollection[0],df), 2.3074607255595923, atol=.01)

def test_interestingness_1_1_0():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y')

    df.setContext([lux.Spec(attribute = "Horsepower"),lux.Spec(attribute = "Year")])
    #check for top recommended Enhance graph
    assert df.recommendation['Enhance'][0].mark == 'scatter'
    assert df.recommendation['Enhance'][0].specLst[0].attribute == 'Horsepower'
    assert df.recommendation['Enhance'][0].specLst[1].attribute == 'Displacement'
    assert df.recommendation['Enhance'][0].specLst[2].attribute == 'Year'

    #check for top recommended Filter graph
    assert df.recommendation['Filter'][0].mark == 'line'
    assert df.recommendation['Filter'][0].specLst[0].attribute == 'Year'
    assert df.recommendation['Filter'][0].specLst[1].attribute == 'Horsepower'
    assert df.recommendation['Filter'][0].specLst[1].aggregation == 'mean'
    assert df.recommendation['Filter'][0].specLst[2].attribute == 'Cylinders'
    assert df.recommendation['Filter'][0].specLst[2].value == 6

    #check for top recommended Generalize graph
    assert df.recommendation['Generalize'][0].mark == 'histogram'
    assert df.recommendation['Generalize'][0].specLst[0].attribute == 'Horsepower'
    assert df.recommendation['Generalize'][0].specLst[1].attribute == 'Record'
    assert df.recommendation['Generalize'][0].specLst[1].aggregation == 'count'

def test_interestingness_1_1_1():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y')

    df.setContext([lux.Spec(attribute = "Horsepower"), lux.Spec(attribute = "Origin", filterOp="=",value = "USA", binSize=20)])
    #check for top recommended Enhance graph
    assert df.recommendation['Enhance'][0].mark == 'bar'
    assert df.recommendation['Enhance'][0].specLst[0].attribute == 'Horsepower'
    assert df.recommendation['Enhance'][0].specLst[0].aggregation == 'mean'
    assert df.recommendation['Enhance'][0].specLst[1].attribute == 'Cylinders'
    assert df.recommendation['Enhance'][0].specLst[2].attribute == 'Origin'
    assert df.recommendation['Enhance'][0].specLst[2].value == 'USA'

    #check for top recommended Filter graph
    assert df.recommendation['Filter'][0].mark == 'histogram'
    assert df.recommendation['Filter'][0].specLst[0].attribute == 'Horsepower'
    assert df.recommendation['Filter'][0].specLst[1].attribute == 'Record'
    assert df.recommendation['Filter'][0].specLst[1].aggregation == 'count'
    assert df.recommendation['Filter'][0].specLst[2].attribute == 'Origin'
    assert df.recommendation['Filter'][0].specLst[2].value == 'Europe'

def test_interestingness_0_2_0():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y')

    df.setContext([lux.Spec(attribute = "Horsepower"),lux.Spec(attribute = "Acceleration")])
    #check for top recommended Enhance graph
    assert df.recommendation['Enhance'][0].mark == 'scatter'
    assert df.recommendation['Enhance'][0].specLst[0].attribute == 'Horsepower'
    assert df.recommendation['Enhance'][0].specLst[1].attribute == 'Acceleration'
    assert df.recommendation['Enhance'][0].specLst[2].attribute == 'Origin'

    #check for top recommended Filter graph
    assert df.recommendation['Filter'][0].mark == 'scatter'
    assert df.recommendation['Filter'][0].specLst[0].attribute == 'Horsepower'
    assert df.recommendation['Filter'][0].specLst[1].attribute == 'Acceleration'
    assert df.recommendation['Filter'][0].specLst[2].attribute == 'Year'
    assert df.recommendation['Filter'][0].specLst[2].dataType == 'temporal'

    #check for top recommended Generalize graph
    assert df.recommendation['Generalize'][0].mark == 'histogram'
    assert df.recommendation['Generalize'][0].specLst[0].attribute == 'Horsepower'
    assert df.recommendation['Generalize'][0].specLst[1].attribute == 'Record'
    assert df.recommendation['Generalize'][0].specLst[1].aggregation == 'count'


def test_interestingness_0_2_1():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y')

    df.setContext([lux.Spec(attribute = "Horsepower"),lux.Spec(attribute = "Acceleration"),lux.Spec(attribute = "Acceleration", filterOp=">",value = 10)])
    # assert np.isclose(interestingness(df.viewCollection[0],df), 0.39945113787283737, atol=.01)
    assert np.isclose(interestingness(df.viewCollection[0], df), 0.39945113787283737, atol=.01)