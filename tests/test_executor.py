from .context import lux
import pytest
import pandas as pd
from lux.executor.PandasExecutor import PandasExecutor
def test_lazyExecution():
    df = pd.read_csv("lux/data/car.csv")
    df.setContext([lux.Spec(attribute = "Horsepower",aggregation="mean"),lux.Spec(attribute = "Origin")])
    # Check data field in view is empty before calling executor
    assert df.view_collection[0].data==None
    PandasExecutor.execute(df.view_collection,df)
    assert type(df.view_collection[0].data) == lux.luxDataFrame.LuxDataframe.LuxDataFrame
    
def test_selection():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y') # change pandas dtype for the column "Year" to datetype
    df.setContext([lux.Spec(attribute = ["Horsepower","Weight","Acceleration"]),lux.Spec(attribute = "Year")])

    PandasExecutor.execute(df.view_collection,df)

    assert all([type(vc.data)==lux.luxDataFrame.LuxDataframe.LuxDataFrame for vc in df.view_collection])
    assert all(df.view_collection[2].data.columns ==["Year",'Acceleration'])

def test_aggregation():
    df = pd.read_csv("lux/data/car.csv")
    df.setContext([lux.Spec(attribute = "Horsepower",aggregation="mean"),lux.Spec(attribute = "Origin")])
    PandasExecutor.execute(df.view_collection,df)
    resultDf = df.view_collection[0].data
    assert int(resultDf[resultDf["Origin"]=="USA"]["Horsepower"])==119

    df.setContext([lux.Spec(attribute = "Horsepower",aggregation="sum"),lux.Spec(attribute = "Origin")])
    PandasExecutor.execute(df.view_collection,df)
    resultDf = df.view_collection[0].data
    assert int(resultDf[resultDf["Origin"]=="Japan"]["Horsepower"])==6307

    df.setContext([lux.Spec(attribute = "Horsepower",aggregation="max"),lux.Spec(attribute = "Origin")])
    PandasExecutor.execute(df.view_collection,df)
    resultDf = df.view_collection[0].data
    assert int(resultDf[resultDf["Origin"]=="Europe"]["Horsepower"])==133
    
def test_filter():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y') # change pandas dtype for the column "Year" to datetype
    df.setContext([lux.Spec(attribute = "Horsepower"),lux.Spec(attribute = "Year"), lux.Spec(attribute = "Origin", filterOp="=",value = "USA")])
    view = df.view_collection[0]
    view.data = df
    PandasExecutor.executeFilter(view)
    assert len(view.data) == len(df[df["Origin"]=="USA"])
def test_inequalityfilter():
    df = pd.read_csv("lux/data/car.csv")
    df.setContext([lux.Spec(attribute = "Horsepower", filterOp=">",value=50),lux.Spec(attribute = "MilesPerGal")])
    view = df.view_collection[0]
    view.data = df
    PandasExecutor.executeFilter(view)
    assert len(df) > len(view.data)
    assert len(view.data) == 386 
    
    df.setContext([lux.Spec(attribute = "Horsepower", filterOp="<=",value=100),lux.Spec(attribute = "MilesPerGal")])
    view = df.view_collection[0]
    view.data = df
    PandasExecutor.executeFilter(view)
    assert len(view.data) == len(df[df["Horsepower"]<=100]) == 242

    # Test end-to-end
    PandasExecutor.execute(df.view_collection,df)
    Nbins =list(filter(lambda x: x.binSize!=0 , df.view_collection[0].spec_lst))[0].binSize
    assert len(df.view_collection[0].data) == Nbins
    
def test_binning():
    df = pd.read_csv("lux/data/car.csv")
    df.setContext([lux.Spec(attribute = "Horsepower")])
    PandasExecutor.execute(df.view_collection,df)
    Nbins =list(filter(lambda x: x.binSize!=0 , df.view_collection[0].spec_lst))[0].binSize
    assert len(df.view_collection[0].data) == Nbins

def test_record():
    df = pd.read_csv("lux/data/car.csv")
    df.setContext([lux.Spec(attribute = "Cylinders")])
    PandasExecutor.execute(df.view_collection,df)
    assert len(df.view_collection[0].data) == len(df["Cylinders"].unique())
    
def test_filter_aggregation_fillzero_aligned():
    df = pd.read_csv("lux/data/car.csv")
    df.setContext([lux.Spec(attribute="Cylinders"),lux.Spec(attribute="MilesPerGal"),lux.Spec("Origin=Japan")])
    PandasExecutor.execute(df.view_collection,df)
    result = df.view_collection[0].data
    externalValidation = df[df["Origin"]=="Japan"].groupby("Cylinders").mean()["MilesPerGal"]
    assert result[result["Cylinders"]==5]["MilesPerGal"].values[0]==0
    assert result[result["Cylinders"]==8]["MilesPerGal"].values[0]==0
    assert result[result["Cylinders"]==3]["MilesPerGal"].values[0]==externalValidation[3]
    assert result[result["Cylinders"]==4]["MilesPerGal"].values[0]==externalValidation[4]
    assert result[result["Cylinders"]==6]["MilesPerGal"].values[0]==externalValidation[6]

def test_exclude_attribute():
    df = pd.read_csv("lux/data/car.csv")
    df.setContext([lux.Spec("?", exclude=["Name", "Year"]),lux.Spec("Horsepower")])
    view = df.view_collection[0]
    view.data = df
    PandasExecutor.executeFilter(view)
    for vc in df.view_collection: 
        assert (vc.getAttrByChannel("x")[0].attribute != "Year")
        assert (vc.getAttrByChannel("x")[0].attribute != "Name")
        assert (vc.getAttrByChannel("y")[0].attribute != "Year")
        assert (vc.getAttrByChannel("y")[0].attribute != "Year") 