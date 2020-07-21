from .context import lux
import pytest
import pandas as pd

from lux.vis.Vis import Vis
def test_vary_filter_val():
    df = pd.read_csv("lux/data/olympic.csv")
    vis = Vis(["Height","SportType=Ball"],df)
    df.set_context_as_vis(vis)
    df._repr_html_()
    assert len(df.recommendation["Filter"]) == len(df["SportType"].unique())-1

def test_index_group():
    df = pd.read_csv("lux/data/college.csv")
    groupbyResult = df.groupby("Region").sum()
    groupbyResult._repr_html_()
    assert list(groupbyResult.recommendation.keys() ) == ['Index-Group', 'Correlation', 'Distribution']