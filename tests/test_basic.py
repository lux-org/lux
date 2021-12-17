
from IPython.core.display import display
from .context import lux
import pytest
import pandas as pd
import numpy as np


class TestBasic:

    def test_basic(self):
        df: lux.LuxDataFrame
        df = pd.DataFrame({"a": np.random.randint(0, 5, size=(
            20,)), "b": np.random.randint(0, 5, size=(20,))})

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

    def test_ipython_display(self):
        df: lux.LuxDataFrame
        df = pd.DataFrame({"a": np.random.randint(0, 5, size=(
            20,)), "b": np.random.randint(0, 5, size=(20,))})

        assert hasattr(df, "lux")

        df._ipython_display_()

    def test_display_widget(self):
        df: lux.LuxDataFrame
        df = pd.DataFrame({"a": np.random.randint(0, 5, size=(
            20,)), "b": np.random.randint(0, 5, size=(20,))})

        assert hasattr(df, "lux")

        display(df.lux.widget)

    def test_rename(self):

        df = pd.DataFrame({"a": np.random.randint(0, 5, size=(
            20,)), "b": np.random.randint(0, 5, size=(20,))})

        df = df.rename(columns={"a": "c"})

        assert "c" in df.columns

    def test_from_lux_object(self):

        df = pd.DataFrame({"a": np.random.randint(0, 5, size=(
            20,)), "b": np.random.randint(0, 5, size=(20,))})

        df.lux._intent = ["x"]

        lux2 = df.lux.from_lux_object("df", df, df.lux)

        assert lux2.df is df.lux.df

    def test_grouby_series(self):

        df = pd.DataFrame(
            dict(x=np.arange(100), c=np.random.choice(7, size=100)))

        df["y"] = df.x ** 2 + 1 + 200 * np.random.normal(size=df.x.shape)
        df["z"] = (100 - df.x) ** 2 + 1 + 200 * \
            np.random.normal(size=df.x.shape)

        gdf = df.groupby("c")
        sg = gdf["x"]

        # def apply_f(x):
        #     return x.mean()

        # res = sg.apply(apply_f)

        res = sg.describe()
