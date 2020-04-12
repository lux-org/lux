from .context import lux
import pytest
import pandas as pd
from lux.executor.PandasExecutor import PandasExecutor
def test_lazyExecution():
    df = pd.read_csv("lux/data/car.csv")
    df.setContext([lux.Spec(attribute = "Horsepower",aggregation="mean"),lux.Spec(attribute = "Origin")])
    # Check data field in view is empty before calling executor
    assert df.viewCollection[0].data==None
    PandasExecutor.execute(df.viewCollection,df)
    assert type(df.viewCollection[0].data) == lux.luxDataFrame.LuxDataframe.LuxDataFrame
    
def test_selection():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y') # change pandas dtype for the column "Year" to datetype
    df.setContext([lux.Spec(attribute = ["Horsepower","Weight","Acceleration"]),lux.Spec(attribute = "Year")])

    PandasExecutor.execute(df.viewCollection,df)

    assert all([type(vc.data)==lux.luxDataFrame.LuxDataframe.LuxDataFrame for vc in df.viewCollection])
    assert all(df.viewCollection[2].data.columns ==["Year",'Acceleration'])

def test_aggregation():
    df = pd.read_csv("lux/data/car.csv")
    df.setContext([lux.Spec(attribute = "Horsepower",aggregation="mean"),lux.Spec(attribute = "Origin")])
    PandasExecutor.execute(df.viewCollection,df)
    resultDf = df.viewCollection[0].data
    assert int(resultDf[resultDf["Origin"]=="USA"]["Horsepower"])==119

    df.setContext([lux.Spec(attribute = "Horsepower",aggregation="sum"),lux.Spec(attribute = "Origin")])
    PandasExecutor.execute(df.viewCollection,df)
    resultDf = df.viewCollection[0].data
    assert int(resultDf[resultDf["Origin"]=="Japan"]["Horsepower"])==6307

    df.setContext([lux.Spec(attribute = "Horsepower",aggregation="max"),lux.Spec(attribute = "Origin")])
    PandasExecutor.execute(df.viewCollection,df)
    resultDf = df.viewCollection[0].data
    assert int(resultDf[resultDf["Origin"]=="Europe"]["Horsepower"])==133
    
def test_filter():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y') # change pandas dtype for the column "Year" to datetype
    df.setContext([lux.Spec(attribute = "Horsepower"),lux.Spec(attribute = "Year"), lux.Spec(attribute = "Origin", filterOp="=",value = "USA")])
    PandasExecutor.executeFilter(df.viewCollection[0],df)
    assert len(df.viewCollection[0].data) == len(df[df["Origin"]=="USA"])
def test_inequalityfilter():
    df = pd.read_csv("lux/data/car.csv")
    df.setContext([lux.Spec(attribute = "Horsepower", filterOp=">",value=50),lux.Spec(attribute = "MilesPerGal")])
    PandasExecutor.execute(df.viewCollection,df)
    assert len(df) > len(df.viewCollection[0].data)

    df.setContext([lux.Spec(attribute = "Horsepower", filterOp="<=",value=100),lux.Spec(attribute = "MilesPerGal")])
    PandasExecutor.execute(df.viewCollection,df)
    assert len(df.viewCollection[0].data) == len(df[df["Horsepower"]<=100]) == 242

def test_binning():
    df = pd.read_csv("lux/data/car.csv")
    df.setContext([lux.Spec(attribute = "Horsepower")])
    PandasExecutor.execute(df.viewCollection,df)