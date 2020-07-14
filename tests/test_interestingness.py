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
    
    df.set_context([lux.VisSpec(attribute = "Origin")])
    df.show_more()
    #check that top recommended enhance graph score is not none and that ordering makes intuitive sense
    assert interestingness(df.recommendation['Enhance'][0],df) != None
    rank1 = -1
    rank2 = -1
    rank3 = -1
    for f in range(0, len(df.recommendation['Enhance'])):
        if df.recommendation['Enhance'][f].spec_lst[0].attribute == 'Displacement':
            rank1 = f
        if df.recommendation['Enhance'][f].spec_lst[0].attribute == 'Weight':
            rank2 = f
        if df.recommendation['Enhance'][f].spec_lst[0].attribute == 'Acceleration':
            rank3 = f
    assert rank1 < rank2 and rank1 < rank3 and rank2 < rank3

    #check that top recommended filter graph score is not none and that ordering makes intuitive sense
    assert interestingness(df.recommendation['Filter'][0],df) != None
    rank1 = -1
    rank2 = -1
    rank3 = -1
    for f in range(0, len(df.recommendation['Filter'])):
        if int(df.recommendation['Filter'][f].spec_lst[2].value) == 8:
            rank1 = f
        if int(df.recommendation['Filter'][f].spec_lst[2].value) == 6:
            rank2 = f
        if '1972' in str(df.recommendation['Filter'][f].spec_lst[2].value):
            rank3 = f
    assert rank1 < rank2 and rank1 < rank3 and rank2 < rank3

# def test_interestingness_1_0_1():
#     df = pd.read_csv("lux/data/car.csv")
#     df["Year"] = pd.to_datetime(df["Year"], format='%Y')
    
#     df.set_context([lux.VisSpec(attribute = "Origin", filter_op="=",value="USA"),lux.VisSpec(attribute = "Origin")])
#     df.show_more()
#     assert interestingness(df.view_collection[0],df) != None

def test_interestingness_0_1_0():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y')

    df.set_context([lux.VisSpec(attribute = "Horsepower")])
    df.show_more()
    #check that top recommended enhance graph score is not none and that ordering makes intuitive sense
    assert interestingness(df.recommendation['Enhance'][0],df) != None
    rank1 = -1
    rank2 = -1
    rank3 = -1
    for f in range(0, len(df.recommendation['Enhance'])):
        if df.recommendation['Enhance'][f].mark == 'scatter' and df.recommendation['Enhance'][f].spec_lst[1].attribute == 'Weight':
            rank1 = f
        if df.recommendation['Enhance'][f].mark == 'scatter' and df.recommendation['Enhance'][f].spec_lst[1].attribute == 'Acceleration':
            rank2 = f
        if df.recommendation['Enhance'][f].mark == 'line' and df.recommendation['Enhance'][f].spec_lst[0].attribute == 'Year':
            rank3 = f
    assert rank1 < rank2 and rank1 < rank3 and rank2 < rank3

    #check that top recommended filter graph score is not none and that ordering makes intuitive sense
    assert interestingness(df.recommendation['Filter'][0],df) != None
    rank1 = -1
    rank2 = -1
    rank3 = -1
    for f in range(0, len(df.recommendation['Filter'])):
        if df.recommendation['Filter'][f].spec_lst[2].value == 4:
            rank1 = f
        if str(df.recommendation['Filter'][f].spec_lst[2].value) == "Europe":
            rank2 = f
        if '1971' in str(df.recommendation['Filter'][f].spec_lst[2].value):
            rank3 = f
    assert rank1 < rank2 and rank1 < rank3 and rank2 < rank3


def test_interestingness_0_1_1():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y')
    
    df.set_context([lux.VisSpec(attribute = "Origin", filter_op="=",value="?"),lux.VisSpec(attribute = "MilesPerGal")])
    df.show_more()
    assert interestingness(df.recommendation['Current Views'][0],df) != None
    assert str(df.recommendation['Current Views'][0].spec_lst[2].value) == 'USA'

def test_interestingness_1_1_0():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y')

    df.set_context([lux.VisSpec(attribute = "Horsepower"),lux.VisSpec(attribute = "Year")])
    df.show_more()
    #check that top recommended Enhance graph score is not none (all graphs here have same score)
    assert interestingness(df.recommendation['Enhance'][0],df) != None

    #check that top recommended filter graph score is not none and that ordering makes intuitive sense
    assert interestingness(df.recommendation['Filter'][0],df) != None
    rank1 = -1
    rank2 = -1
    rank3 = -1
    for f in range(0, len(df.recommendation['Filter'])):
        if df.recommendation['Filter'][f].spec_lst[2].value == 6:
            rank1 = f
        if str(df.recommendation['Filter'][f].spec_lst[2].value) == "Europe":
            rank2 = f
        if df.recommendation['Filter'][f].spec_lst[2].value == 5:
            rank3 = f
    assert rank1 < rank2 and rank1 < rank3 and rank2 < rank3

    #check that top recommended generalize graph score is not none
    assert interestingness(df.recommendation['Filter'][0],df) != None

def test_interestingness_1_1_1():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y')

    df.set_context([lux.VisSpec(attribute = "Horsepower"), lux.VisSpec(attribute = "Origin", filter_op="=",value = "USA", bin_size=20)])
    df.show_more()
    #check that top recommended Enhance graph score is not none and that ordering makes intuitive sense
    assert interestingness(df.recommendation['Enhance'][0],df) != None
    rank1 = -1
    rank2 = -1
    rank3 = -1
    for f in range(0, len(df.recommendation['Enhance'])):
        if str(df.recommendation['Enhance'][f].spec_lst[2].value) == "USA" and str(df.recommendation['Enhance'][f].spec_lst[1].attribute) == 'Cylinders':
            rank1 = f
        if str(df.recommendation['Enhance'][f].spec_lst[2].value) == "USA" and str(df.recommendation['Enhance'][f].spec_lst[1].attribute) == 'Weight':
            rank2 = f
        if str(df.recommendation['Enhance'][f].spec_lst[2].value) == "USA" and str(df.recommendation['Enhance'][f].spec_lst[1].attribute) == 'Horsepower':
            rank3 = f
    assert rank1 < rank2 and rank1 < rank3 and rank2 < rank3

    #check for top recommended Filter graph score is not none
    assert interestingness(df.recommendation['Filter'][0],df) != None

def test_interestingness_0_2_0():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y')

    df.set_context([lux.VisSpec(attribute = "Horsepower"),lux.VisSpec(attribute = "Acceleration")])
    df.show_more()
    #check that top recommended enhance graph score is not none and that ordering makes intuitive sense
    assert interestingness(df.recommendation['Enhance'][0],df) != None
    rank1 = -1
    rank2 = -1
    rank3 = -1
    for f in range(0, len(df.recommendation['Enhance'])):
        if str(df.recommendation['Enhance'][f].spec_lst[2].attribute) == "Origin" and str(df.recommendation['Enhance'][f].mark) == 'scatter':
            rank1 = f
        if str(df.recommendation['Enhance'][f].spec_lst[2].attribute) == "Displacement" and str(df.recommendation['Enhance'][f].mark) == 'scatter':
            rank2 = f
        if str(df.recommendation['Enhance'][f].spec_lst[2].attribute) == "Year" and str(df.recommendation['Enhance'][f].mark) == 'scatter':
            rank3 = f
    assert rank1 < rank2 and rank1 < rank3 and rank2 < rank3

    #check that top recommended filter graph score is not none and that ordering makes intuitive sense
    assert interestingness(df.recommendation['Filter'][0],df) != None
    rank1 = -1
    rank2 = -1
    rank3 = -1
    for f in range(0, len(df.recommendation['Filter'])):
        if '1973' in str(df.recommendation['Filter'][f].spec_lst[2].value):
            rank1 = f
        if '1976' in str(df.recommendation['Filter'][f].spec_lst[2].value):
            rank2 = f
        if str(df.recommendation['Filter'][f].spec_lst[2].value) == "Europe":
            rank3 = f
    assert rank1 < rank2 and rank1 < rank3 and rank2 < rank3

    #check that top recommended Generalize graph score is not none
    assert interestingness(df.recommendation['Generalize'][0],df) != None


def test_interestingness_0_2_1():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y')

    df.set_context([lux.VisSpec(attribute = "Horsepower"),lux.VisSpec(attribute = "Acceleration"),lux.VisSpec(attribute = "Acceleration", filter_op=">",value = 10)])
    df.show_more()
    #check that top recommended Generalize graph score is not none
    assert interestingness(df.recommendation['Generalize'][0],df) != None