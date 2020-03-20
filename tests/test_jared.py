from .context import lux
import pytest
import pandas as pd

def test_badContext():
    df = pd.read_csv("lux/data/car.csv")
    try:
        df.setContext([lux.Spec("Origin=?"),lux.Spec(attribute = "NonExistentAttribute")])
        assert False
    except:
        assert True

def test_computeStats():
    df = pd.read_csv("lux/data/car.csv")

    # Stats should automatically be computed
    # df.computeStats()
    
    for column in df.columns:
        assert len(pd.Series(df.uniqueValues[column]).drop_duplicates()) == df.cardinality[column]

def test_computeDatasetMetadata():
    df = pd.read_csv("lux/data/car.csv")

    print(df.dataType)
    
    assert False


