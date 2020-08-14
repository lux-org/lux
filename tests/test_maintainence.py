
from .context import lux
import pytest
import pandas as pd
from lux.vis.Vis import Vis

def test_metadata_subsequent_display():
    df = pd.read_csv("lux/data/car.csv")
    df._repr_html_()
    assert df._metadata_fresh==True, "Failed to maintain metadata after display df"
    df._repr_html_()
    assert df._metadata_fresh==True, "Failed to maintain metadata after display df"

def test_metadata_subsequent_vis():
    df = pd.read_csv("lux/data/car.csv")
    df._repr_html_()
    assert df._metadata_fresh==True, "Failed to maintain metadata after display df"
    vis = Vis(["Acceleration","Horsepower"],df)
    assert df._metadata_fresh==True, "Failed to maintain metadata after display df"

def test_metadata_inplace_operation():
    df = pd.read_csv("lux/data/car.csv")
    df._repr_html_()
    assert df._metadata_fresh==True, "Failed to maintain metadata after display df"
    df.dropna(inplace=True)
    assert df._metadata_fresh==False, "Failed to expire metadata after in-place Pandas operation"

def test_metadata_new_df_operation():
    df = pd.read_csv("lux/data/car.csv")
    df._repr_html_()
    assert df._metadata_fresh==True, "Failed to maintain metadata after display df"
    df[["MilesPerGal","Acceleration"]]
    assert df._metadata_fresh==True, "Failed to maintain metadata after display df"
    df2 = df[["MilesPerGal","Acceleration"]]
    assert not hasattr(df2,"_metadata_fresh")

def test_metadata_column_group_reset_df():
    df = pd.read_csv("lux/data/car.csv")
    assert not hasattr(df,"_metadata_fresh")
    result = df.groupby("Cylinders").mean()
    assert not hasattr(result,"_metadata_fresh")
    result._repr_html_() # Note that this should trigger two compute metadata (one for df, and one for an intermediate df.reset_index used to feed inside created Vis)
    assert result._metadata_fresh==True, "Failed to maintain metadata after display df"
    
def test_recs_inplace_operation():
    df = pd.read_csv("lux/data/car.csv")
    df._repr_html_()
    assert df._recs_fresh==True, "Failed to maintain recommendation after display df"
    assert len(df.recommendation["Occurrence"])==3
    df.drop(columns=["Name"],inplace=True)
    assert 'Name' not in df.columns, "Failed to perform `drop` operation in-place"
    assert df._recs_fresh==False, "Failed to maintain recommendation after in-place Pandas operation"
    df._repr_html_()
    assert len(df.recommendation["Occurrence"])==2
    assert df._recs_fresh==True, "Failed to maintain recommendation after display df"