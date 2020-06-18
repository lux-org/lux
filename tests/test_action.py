from .context import lux
import pytest
import pandas as pd

from lux.view.View import View
def test_vary_filter_val():
    df = pd.read_csv("lux/data/olympic.csv")
    view = View(["Height","SportType=Ball"])
    view = view.load(df)
    df.setContextAsView(view)
    df.showMore()
    assert len(df.recommendation["Filter"]) == len(df["SportType"].unique())-1