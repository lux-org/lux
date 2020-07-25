from .context import lux
import pytest
import pandas as pd

from lux.vis.Vis import Vis
def test_vary_filter_val():
    df = pd.read_csv("lux/data/olympic.csv")
    vis = Vis(["Height","SportType=Ball"],df)
    df.set_intent_as_vis(vis)
    df._repr_html_()
    assert len(df.recommendation["Filter"]) == len(df["SportType"].unique())-1


def test_row_column_group():
    df = pd.read_csv("lux/data/state_timeseries.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    tseries = df.pivot(index="State",columns="Date",values="Value")
    # Interpolating missing values
    tseries[tseries.columns.min()] = tseries[tseries.columns.min()].fillna(0)
    tseries[tseries.columns.max()] = tseries[tseries.columns.max()].fillna(tseries.max(axis=1))
    tseries = tseries.interpolate('zero',axis=1)
    tseries._repr_html_()
    assert list(tseries.recommendation.keys() ) == ['Row Groups','Column Groups']

def test_groupby():
    df = pd.read_csv("lux/data/college.csv")
    groupbyResult = df.groupby("Region").sum()
    groupbyResult._repr_html_()
    assert list(groupbyResult.recommendation.keys() ) == ['Column Groups']

def test_crosstab():
    # Example from http://www.datasciencemadesimple.com/cross-tab-cross-table-python-pandas/
    d = {
        'Name':['Alisa','Bobby','Cathrine','Alisa','Bobby','Cathrine',
                'Alisa','Bobby','Cathrine','Alisa','Bobby','Cathrine'],
        'Exam':['Semester 1','Semester 1','Semester 1','Semester 1','Semester 1','Semester 1',
                'Semester 2','Semester 2','Semester 2','Semester 2','Semester 2','Semester 2'],
        
        'Subject':['Mathematics','Mathematics','Mathematics','Science','Science','Science',
                'Mathematics','Mathematics','Mathematics','Science','Science','Science'],
    'Result':['Pass','Pass','Fail','Pass','Fail','Pass','Pass','Fail','Fail','Pass','Pass','Fail']}
    
    df = pd.DataFrame(d,columns=['Name','Exam','Subject','Result'])
    result = pd.crosstab([df.Exam],df.Result)
    result._repr_html_()
    assert list(result.recommendation.keys() ) == ['Row Groups','Column Groups']