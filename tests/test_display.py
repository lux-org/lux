from .context import lux
import pytest
import pandas as pd

def test_toPandas():
    df = pd.read_csv("lux/data/car.csv")
    df.toPandas()

def test_display():
    df = pd.read_csv("lux/data/car.csv")
    df._repr_html_()
    