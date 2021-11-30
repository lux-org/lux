
from .context import lux
import pytest
import pandas as pd


class TestBasic:

    def test_basic(self):
        df: lux.LuxDataFrame
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

        assert hasattr(df, "lux")

        df.lux.intent = ["a"]

        assert df.lux.intent[0].attribute == "a"

        assert df._LUX_ == df.lux

        # force re-consolidation of series
        df["a"] += 1

        series = df["a"]

        assert hasattr(series, "lux")
        assert series.lux._intent is not None
        assert series.lux._intent[0].attribute == "a"

    def test_basic(self):
        df: lux.LuxDataFrame
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

        assert hasattr(df, "lux")

        df._ipython_display_()
