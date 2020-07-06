from .context import lux
import pytest
import pandas as pd

def test_to_pandas():
    df = pd.read_csv("lux/data/car.csv")
    df.to_pandas()

def test_display_LuxDataframe():
    df = pd.read_csv("lux/data/car.csv")
    df._repr_html_()
    
def test_display_ViewCollection():
    df = pd.read_csv("lux/data/car.csv")
    df.showMore()
    df.recommendation["Correlation"]._repr_html_()
    
def test_display_View():
    df = pd.read_csv("lux/data/car.csv")
    df.showMore()
    df.recommendation["Correlation"][0]._repr_html_()
    