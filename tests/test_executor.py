from .context import lux
import pytest
import pandas as pd
from lux.executor.PandasExecutor import PandasExecutor
def test_lazy_execution():
    df = pd.read_csv("lux/data/car.csv")
    df.set_context([lux.Spec(attribute ="Horsepower", aggregation="mean"), lux.Spec(attribute ="Origin")])
    # Check data field in view is empty before calling executor
    assert df.current_view[0].data == None
    PandasExecutor.execute(df.current_view, df)
    assert type(df.current_view[0].data) == lux.luxDataFrame.LuxDataframe.LuxDataFrame
    
def test_selection():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y') # change pandas dtype for the column "Year" to datetype
    df.set_context([lux.Spec(attribute = ["Horsepower", "Weight", "Acceleration"]), lux.Spec(attribute ="Year")])

    PandasExecutor.execute(df.current_view, df)

    assert all([type(vc.data) == lux.luxDataFrame.LuxDataframe.LuxDataFrame for vc in df.current_view])
    assert all(df.current_view[2].data.columns == ["Year", 'Acceleration'])

def test_aggregation():
    df = pd.read_csv("lux/data/car.csv")
    df.set_context([lux.Spec(attribute ="Horsepower", aggregation="mean"), lux.Spec(attribute ="Origin")])
    PandasExecutor.execute(df.current_view, df)
    result_df = df.current_view[0].data
    assert int(result_df[result_df["Origin"]=="USA"]["Horsepower"])==119

    df.set_context([lux.Spec(attribute ="Horsepower", aggregation="sum"), lux.Spec(attribute ="Origin")])
    PandasExecutor.execute(df.current_view, df)
    result_df = df.current_view[0].data
    assert int(result_df[result_df["Origin"]=="Japan"]["Horsepower"])==6307

    df.set_context([lux.Spec(attribute ="Horsepower", aggregation="max"), lux.Spec(attribute ="Origin")])
    PandasExecutor.execute(df.current_view, df)
    result_df = df.current_view[0].data
    assert int(result_df[result_df["Origin"]=="Europe"]["Horsepower"])==133
    
def test_filter():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y') # change pandas dtype for the column "Year" to datetype
    df.set_context([lux.Spec(attribute ="Horsepower"), lux.Spec(attribute ="Year"), lux.Spec(attribute ="Origin", filter_op="=", value ="USA")])
    view = df.current_view[0]
    view.data = df
    PandasExecutor.execute_filter(view)
    assert len(view.data) == len(df[df["Origin"]=="USA"])
def test_inequalityfilter():
    df = pd.read_csv("lux/data/car.csv")
    df.set_context([lux.Spec(attribute ="Horsepower", filter_op=">", value=50), lux.Spec(attribute ="MilesPerGal")])
    view = df.current_view[0]
    view.data = df
    PandasExecutor.execute_filter(view)
    assert len(df) > len(view.data)
    assert len(view.data) == 386 
    
    df.set_context([lux.Spec(attribute ="Horsepower", filter_op="<=", value=100), lux.Spec(attribute ="MilesPerGal")])
    view = df.current_view[0]
    view.data = df
    PandasExecutor.execute_filter(view)
    assert len(view.data) == len(df[df["Horsepower"]<=100]) == 242

    # Test end-to-end
    PandasExecutor.execute(df.current_view, df)
    Nbins =list(filter(lambda x: x.bin_size!=0, df.current_view[0].spec_lst))[0].bin_size
    assert len(df.current_view[0].data) == Nbins
    
def test_binning():
    df = pd.read_csv("lux/data/car.csv")
    df.set_context([lux.Spec(attribute ="Horsepower")])
    PandasExecutor.execute(df.current_view, df)
    nbins =list(filter(lambda x: x.bin_size!=0, df.current_view[0].spec_lst))[0].bin_size
    assert len(df.current_view[0].data) == nbins

def test_record():
    df = pd.read_csv("lux/data/car.csv")
    df.set_context([lux.Spec(attribute ="Cylinders")])
    PandasExecutor.execute(df.current_view, df)
    assert len(df.current_view[0].data) == len(df["Cylinders"].unique())
    
def test_filter_aggregation_fillzero_aligned():
    df = pd.read_csv("lux/data/car.csv")
    df.set_context([lux.Spec(attribute="Cylinders"), lux.Spec(attribute="MilesPerGal"), lux.Spec("Origin=Japan")])
    PandasExecutor.execute(df.current_view, df)
    result = df.current_view[0].data
    externalValidation = df[df["Origin"]=="Japan"].groupby("Cylinders").mean()["MilesPerGal"]
    assert result[result["Cylinders"]==5]["MilesPerGal"].values[0]==0
    assert result[result["Cylinders"]==8]["MilesPerGal"].values[0]==0
    assert result[result["Cylinders"]==3]["MilesPerGal"].values[0]==externalValidation[3]
    assert result[result["Cylinders"]==4]["MilesPerGal"].values[0]==externalValidation[4]
    assert result[result["Cylinders"]==6]["MilesPerGal"].values[0]==externalValidation[6]

def test_exclude_attribute():
    df = pd.read_csv("lux/data/car.csv")
    df.set_context([lux.Spec("?", exclude=["Name", "Year"]), lux.Spec("Horsepower")])
    view = df.current_view[0]
    view.data = df
    PandasExecutor.execute_filter(view)
    for vc in df.current_view:
        assert (vc.get_attr_by_channel("x")[0].attribute != "Year")
        assert (vc.get_attr_by_channel("x")[0].attribute != "Name")
        assert (vc.get_attr_by_channel("y")[0].attribute != "Year")
        assert (vc.get_attr_by_channel("y")[0].attribute != "Year") 
