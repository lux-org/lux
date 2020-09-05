from .context import lux
import pytest
import pandas as pd
from lux.vis.Vis import Vis
from lux.vis.VisList import VisList
def test_to_pandas():
    df = pd.read_csv("lux/data/car.csv")
    df.to_pandas()

def test_display_LuxDataframe():
    df = pd.read_csv("lux/data/car.csv")
    df._repr_html_()
    
def test_display_Vis():
    df = pd.read_csv("lux/data/car.csv")
    vis = Vis(["Horsepower","Acceleration"],df)
    vis._repr_html_()
    
def test_display_VisList():
    df = pd.read_csv("lux/data/car.csv")
    vislist = VisList(["?","Acceleration"],df)
    vislist._repr_html_()