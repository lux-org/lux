from .context import lux
import pytest
import pandas as pd
from lux.executor.PandasExecutor import PandasExecutor
def test_lazy_execution():
    df = pd.read_csv("lux/data/car.csv")
    df.set_intent([lux.Clause(attribute ="Horsepower", aggregation="mean"), lux.Clause(attribute ="Origin")])
    # Check data field in vis is empty before calling executor
    assert df.current_vis[0].data == None
    PandasExecutor.execute(df.current_vis, df)
    assert type(df.current_vis[0].data) == lux.luxDataFrame.LuxDataframe.LuxDataFrame
    
def test_selection():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y') # change pandas dtype for the column "Year" to datetype
    df.set_intent([lux.Clause(attribute = ["Horsepower", "Weight", "Acceleration"]), lux.Clause(attribute ="Year")])

    PandasExecutor.execute(df.current_vis, df)

    assert all([type(vc.data) == lux.luxDataFrame.LuxDataframe.LuxDataFrame for vc in df.current_vis])
    assert all(df.current_vis[2].data.columns == ["Year", 'Acceleration'])

def test_aggregation():
    df = pd.read_csv("lux/data/car.csv")
    df.set_intent([lux.Clause(attribute ="Horsepower", aggregation="mean"), lux.Clause(attribute ="Origin")])
    PandasExecutor.execute(df.current_vis, df)
    result_df = df.current_vis[0].data
    assert int(result_df[result_df["Origin"]=="USA"]["Horsepower"])==119

    df.set_intent([lux.Clause(attribute ="Horsepower", aggregation="sum"), lux.Clause(attribute ="Origin")])
    PandasExecutor.execute(df.current_vis, df)
    result_df = df.current_vis[0].data
    assert int(result_df[result_df["Origin"]=="Japan"]["Horsepower"])==6307

    df.set_intent([lux.Clause(attribute ="Horsepower", aggregation="max"), lux.Clause(attribute ="Origin")])
    PandasExecutor.execute(df.current_vis, df)
    result_df = df.current_vis[0].data
    assert int(result_df[result_df["Origin"]=="Europe"]["Horsepower"])==133

def test_colored_bar_chart():
    from lux.vis.Vis import Vis
    from lux.vis.Vis import Clause
    df = pd.read_csv("lux/data/car.csv")

    x_clause = Clause(attribute = "MilesPerGal", channel = "x")
    y_clause = Clause(attribute = "Origin", channel = "y")
    color_clause = Clause(attribute = 'Cylinders', channel = "color")

    new_vis = Vis([x_clause, y_clause, color_clause])
    new_vis.refresh_source(df)
    #make sure dimention of the data is correct
    color_cardinality = len(df.unique_values['Cylinders'])
    group_by_cardinality = len(df.unique_values['Origin'])
    assert (len(new_vis.data.columns)==3)
    assert(len(new_vis.data)==color_cardinality*group_by_cardinality)

def test_colored_line_chart():
    from lux.vis.Vis import Vis
    from lux.vis.Vis import Clause
    df = pd.read_csv("lux/data/car.csv")

    x_clause = Clause(attribute = "Year", channel = "x")
    y_clause = Clause(attribute = "MilesPerGal", channel = "y")
    color_clause = Clause(attribute = 'Cylinders', channel = "color")

    new_vis = Vis([x_clause, y_clause, color_clause])
    new_vis.refresh_source(df)
    #make sure dimention of the data is correct
    color_cardinality = len(df.unique_values['Cylinders'])
    group_by_cardinality = len(df.unique_values['Year'])
    assert (len(new_vis.data.columns)==3)
    assert(len(new_vis.data)==color_cardinality*group_by_cardinality)
    
def test_filter():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format='%Y') # change pandas dtype for the column "Year" to datetype
    df.set_intent([lux.Clause(attribute ="Horsepower"), lux.Clause(attribute ="Year"), lux.Clause(attribute ="Origin", filter_op="=", value ="USA")])
    vis = df.current_vis[0]
    vis.data = df
    PandasExecutor.execute_filter(vis)
    assert len(vis.data) == len(df[df["Origin"]=="USA"])
def test_inequalityfilter():
    df = pd.read_csv("lux/data/car.csv")
    df.set_intent([lux.Clause(attribute ="Horsepower", filter_op=">", value=50), lux.Clause(attribute ="MilesPerGal")])
    vis = df.current_vis[0]
    vis.data = df
    PandasExecutor.execute_filter(vis)
    assert len(df) > len(vis.data)
    assert len(vis.data) == 386 
    
    df.set_intent([lux.Clause(attribute ="Horsepower", filter_op="<=", value=100), lux.Clause(attribute ="MilesPerGal")])
    vis = df.current_vis[0]
    vis.data = df
    PandasExecutor.execute_filter(vis)
    assert len(vis.data) == len(df[df["Horsepower"]<=100]) == 242

    # Test end-to-end
    PandasExecutor.execute(df.current_vis, df)
    Nbins =list(filter(lambda x: x.bin_size!=0, df.current_vis[0]._inferred_intent))[0].bin_size
    assert len(df.current_vis[0].data) == Nbins
    
def test_binning():
    df = pd.read_csv("lux/data/car.csv")
    df.set_intent([lux.Clause(attribute ="Horsepower")])
    PandasExecutor.execute(df.current_vis, df)
    nbins =list(filter(lambda x: x.bin_size!=0, df.current_vis[0]._inferred_intent))[0].bin_size
    assert len(df.current_vis[0].data) == nbins

def test_record():
    df = pd.read_csv("lux/data/car.csv")
    df.set_intent([lux.Clause(attribute ="Cylinders")])
    PandasExecutor.execute(df.current_vis, df)
    assert len(df.current_vis[0].data) == len(df["Cylinders"].unique())
    
def test_filter_aggregation_fillzero_aligned():
    df = pd.read_csv("lux/data/car.csv")
    df.set_intent([lux.Clause(attribute="Cylinders"), lux.Clause(attribute="MilesPerGal"), lux.Clause("Origin=Japan")])
    PandasExecutor.execute(df.current_vis, df)
    result = df.current_vis[0].data
    externalValidation = df[df["Origin"]=="Japan"].groupby("Cylinders").mean()["MilesPerGal"]
    assert result[result["Cylinders"]==5]["MilesPerGal"].values[0]==0
    assert result[result["Cylinders"]==8]["MilesPerGal"].values[0]==0
    assert result[result["Cylinders"]==3]["MilesPerGal"].values[0]==externalValidation[3]
    assert result[result["Cylinders"]==4]["MilesPerGal"].values[0]==externalValidation[4]
    assert result[result["Cylinders"]==6]["MilesPerGal"].values[0]==externalValidation[6]

def test_exclude_attribute():
    df = pd.read_csv("lux/data/car.csv")
    df.set_intent([lux.Clause("?", exclude=["Name", "Year"]), lux.Clause("Horsepower")])
    vis = df.current_vis[0]
    vis.data = df
    PandasExecutor.execute_filter(vis)
    for vc in df.current_vis:
        assert (vc.get_attr_by_channel("x")[0].attribute != "Year")
        assert (vc.get_attr_by_channel("x")[0].attribute != "Name")
        assert (vc.get_attr_by_channel("y")[0].attribute != "Year")
        assert (vc.get_attr_by_channel("y")[0].attribute != "Year") 
