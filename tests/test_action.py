from .context import lux
import pytest
import pandas as pd

from lux.vis.Vis import Vis
def test_vary_filter_val():
    df = pd.read_csv("lux/data/olympic.csv")
    vis = Vis(["Height","SportType=Ball"],df)
    df.set_context_as_vis(vis)
    df.show_more()
    assert len(df.recommendation["Filter"]) == len(df["SportType"].unique())-1