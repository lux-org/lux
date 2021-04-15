#  Copyright 2019-2020 The Lux Authors.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from .context import lux
import pytest
import pandas as pd
import numpy as np
import psycopg2
from lux.interestingness.interestingness import interestingness


# The following test cases are labelled for vis with <Ndim, Nmsr, Nfilter>
def test_interestingness_1_0_0(global_var):
    df = pytest.car_df
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")

    df.set_intent([lux.Clause(attribute="Origin")])
    df._ipython_display_()
    # check that top recommended enhance graph score is not none and that ordering makes intuitive sense
    assert interestingness(df.recommendation["Enhance"][0], df) != None
    rank1 = -1
    rank2 = -1
    rank3 = -1
    for f in range(0, len(df.recommendation["Enhance"])):
        vis = df.recommendation["Enhance"][f]
        if vis.get_attr_by_channel("x")[0].attribute == "Displacement":
            rank1 = f
        if vis.get_attr_by_channel("x")[0].attribute == "Weight":
            rank2 = f
        if vis.get_attr_by_channel("x")[0].attribute == "Acceleration":
            rank3 = f
    assert rank1 < rank2 and rank1 < rank3 and rank2 < rank3

    # check that top recommended filter graph score is not none and that ordering makes intuitive sense
    assert interestingness(df.recommendation["Filter"][0], df) != None
    rank1 = -1
    rank2 = -1
    rank3 = -1
    for f in range(0, len(df.recommendation["Filter"])):
        vis = df.recommendation["Filter"][f]
        if len(vis.get_attr_by_attr_name("Cylinders")) > 0:
            if int(vis._inferred_intent[2].value) == 8:
                rank1 = f
            if int(vis._inferred_intent[2].value) == 6:
                rank3 = f
        if "ford" in str(df.recommendation["Filter"][f]._inferred_intent[2].value):
            rank2 = f
    assert rank1 < rank2 and rank1 < rank3 and rank2 < rank3
    df.clear_intent()


def test_interestingness_1_0_1(global_var):
    df = pytest.car_df
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")

    df.set_intent(
        [
            lux.Clause(attribute="Origin", filter_op="=", value="USA"),
            lux.Clause(attribute="Cylinders"),
        ]
    )
    df._ipython_display_()
    assert df.current_vis[0].score == 0
    df.clear_intent()


def test_interestingness_0_1_0(global_var):
    lux.config.set_executor_type("Pandas")
    df = pytest.car_df
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")

    df.set_intent([lux.Clause(attribute="Horsepower")])
    df._ipython_display_()
    # check that top recommended enhance graph score is not none and that ordering makes intuitive sense
    assert interestingness(df.recommendation["Enhance"][0], df) != None
    rank1 = -1
    rank2 = -1
    rank3 = -1
    for f in range(0, len(df.recommendation["Enhance"])):
        if (
            df.recommendation["Enhance"][f].mark == "scatter"
            and df.recommendation["Enhance"][f]._inferred_intent[1].attribute == "Weight"
        ):
            rank1 = f
        if (
            df.recommendation["Enhance"][f].mark == "scatter"
            and df.recommendation["Enhance"][f]._inferred_intent[1].attribute == "Acceleration"
        ):
            rank2 = f
        if (
            df.recommendation["Enhance"][f].mark == "line"
            and df.recommendation["Enhance"][f]._inferred_intent[0].attribute == "Year"
        ):
            rank3 = f
    assert rank1 < rank2 and rank1 < rank3 and rank2 < rank3

    # check that top recommended filter graph score is not none and that ordering makes intuitive sense
    assert interestingness(df.recommendation["Filter"][0], df) != None
    rank1 = -1
    rank2 = -1
    rank3 = -1
    for f in range(0, len(df.recommendation["Filter"])):
        if df.recommendation["Filter"][f]._inferred_intent[2].value == 4:
            rank1 = f
        if str(df.recommendation["Filter"][f]._inferred_intent[2].value) == "Europe":
            rank2 = f
        if "1970" in str(df.recommendation["Filter"][f]._inferred_intent[2].value):
            rank3 = f
    assert rank1 < rank2 and rank1 < rank3 and rank2 < rank3
    df.clear_intent()


def test_interestingness_0_1_1(global_var):
    df = pytest.car_df
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")

    df.set_intent(
        [
            lux.Clause(attribute="Origin", filter_op="=", value="?"),
            lux.Clause(attribute="MilesPerGal"),
        ]
    )
    df._ipython_display_()
    assert interestingness(df.recommendation["Current Vis"][0], df) != None
    assert str(df.recommendation["Current Vis"][0]._inferred_intent[2].value) == "USA"
    df.clear_intent()


def test_interestingness_1_1_0(global_var):
    lux.config.set_executor_type("Pandas")
    df = pytest.car_df
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")

    df.set_intent([lux.Clause(attribute="Horsepower"), lux.Clause(attribute="Year")])
    df._ipython_display_()
    # check that top recommended Enhance graph score is not none (all graphs here have same score)
    assert interestingness(df.recommendation["Enhance"][0], df) != None

    # check that top recommended filter graph score is not none and that ordering makes intuitive sense
    assert interestingness(df.recommendation["Filter"][0], df) != None
    rank1 = -1
    rank2 = -1
    rank3 = -1
    for f in range(0, len(df.recommendation["Filter"])):
        vis = df.recommendation["Filter"][f]
        if len(vis.get_attr_by_attr_name("Cylinders")) > 0:
            if int(vis._inferred_intent[2].value) == 6:
                rank1 = f
            if int(vis._inferred_intent[2].value) == 8:
                rank2 = f
        if len(vis.get_attr_by_attr_name("Origin")) > 0:
            if str(vis._inferred_intent[2].value) == "Europe":
                rank3 = f
    assert rank1 < rank2 and rank1 < rank3 and rank2 < rank3

    # check that top recommended generalize graph score is not none
    assert interestingness(df.recommendation["Filter"][0], df) != None
    df.clear_intent()


def test_interestingness_1_1_1(global_var):
    df = pytest.car_df
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")

    df.set_intent(
        [
            lux.Clause(attribute="Horsepower"),
            lux.Clause(attribute="Origin", filter_op="=", value="USA", bin_size=20),
        ]
    )
    df._ipython_display_()
    # check that top recommended Enhance graph score is not none and that ordering makes intuitive sense
    assert interestingness(df.recommendation["Enhance"][0], df) != None
    rank1 = -1
    rank2 = -1
    rank3 = -1
    for f in range(0, len(df.recommendation["Enhance"])):
        if (
            str(df.recommendation["Enhance"][f]._inferred_intent[2].value) == "USA"
            and str(df.recommendation["Enhance"][f]._inferred_intent[1].attribute) == "Cylinders"
        ):
            rank1 = f
        if (
            str(df.recommendation["Enhance"][f]._inferred_intent[2].value) == "USA"
            and str(df.recommendation["Enhance"][f]._inferred_intent[1].attribute) == "Weight"
        ):
            rank2 = f
        if (
            str(df.recommendation["Enhance"][f]._inferred_intent[2].value) == "USA"
            and str(df.recommendation["Enhance"][f]._inferred_intent[1].attribute) == "Horsepower"
        ):
            rank3 = f
    assert rank1 < rank2 and rank1 < rank3 and rank2 < rank3

    # check for top recommended Filter graph score is not none
    assert interestingness(df.recommendation["Filter"][0], df) != None
    df.clear_intent()


def test_interestingness_1_2_0(global_var):
    from lux.vis.Vis import Vis
    from lux.vis.Vis import Clause
    from lux.interestingness.interestingness import interestingness

    lux.config.set_executor_type("Pandas")
    df = pytest.car_df
    y_clause = Clause(attribute="Name", channel="y")
    color_clause = Clause(attribute="Cylinders", channel="color")

    new_vis = Vis([y_clause, color_clause])
    new_vis.refresh_source(df)
    new_vis
    # assert(len(new_vis.data)==color_cardinality*group_by_cardinality)

    assert interestingness(new_vis, df) < 0.01


def test_interestingness_0_2_0(global_var):
    df = pytest.car_df
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")

    df.set_intent([lux.Clause(attribute="Horsepower"), lux.Clause(attribute="Acceleration")])
    df._ipython_display_()
    # check that top recommended enhance graph score is not none and that ordering makes intuitive sense
    assert interestingness(df.recommendation["Enhance"][0], df) != None
    rank1 = -1
    rank2 = -1
    for f in range(0, len(df.recommendation["Enhance"])):
        if (
            str(df.recommendation["Enhance"][f]._inferred_intent[2].attribute) == "Origin"
            and str(df.recommendation["Enhance"][f].mark) == "scatter"
        ):
            rank1 = f
        if (
            str(df.recommendation["Enhance"][f]._inferred_intent[2].attribute) == "Displacement"
            and str(df.recommendation["Enhance"][f].mark) == "scatter"
        ):
            rank2 = f
    assert rank1 < rank2

    # check that top recommended filter graph score is not none and that ordering makes intuitive sense
    assert interestingness(df.recommendation["Filter"][0], df) != None
    # check that top recommended Generalize graph score is not none
    assert interestingness(df.recommendation["Generalize"][0], df) != None
    df.clear_intent()


def test_interestingness_0_2_1(global_var):
    df = pytest.car_df
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")

    df.set_intent(
        [
            lux.Clause(attribute="Horsepower"),
            lux.Clause(attribute="MilesPerGal"),
            lux.Clause(attribute="Acceleration", filter_op=">", value=10),
        ]
    )
    df._ipython_display_()
    # check that top recommended Generalize graph score is not none
    assert interestingness(df.recommendation["Generalize"][0], df) != None
    df.clear_intent()


def test_interestingness_deviation_nan():
    import numpy as np

    dataset = [
        {"date": "2017-08-25", "category": "A", "value": 25.0},
        {"date": "2017-08-25", "category": "B", "value": 1.2},
        {"date": "2017-08-25", "category": "C", "value": 1.3},
        {"date": "2017-08-25", "category": "D", "value": 1.4},
        {"date": "2017-08-25", "category": "E", "value": 1.5},
        {"date": "2017-08-25", "category": "F", "value": 0.1},
        {"date": np.nan, "category": "C", "value": 0.2},
        {"date": np.nan, "category": "B", "value": 0.2},
        {"date": np.nan, "category": "F", "value": 0.3},
        {"date": np.nan, "category": "E", "value": 0.3},
        {"date": np.nan, "category": "D", "value": 0.4},
        {"date": np.nan, "category": "A", "value": 10.4},
        {"date": "2017-07-25", "category": "A", "value": 15.5},
        {"date": "2017-07-25", "category": "F", "value": 1.0},
        {"date": "2017-07-25", "category": "B", "value": 0.1},
    ]
    test = pd.DataFrame(dataset)
    from lux.vis.Vis import Vis

    test["date"] = pd.to_datetime(test["date"], format="%Y-%M-%d")
    test.set_data_type({"value": "quantitative"})

    vis = Vis(["date", "value", "category=A"], test)
    vis2 = Vis(["date", "value", "category=B"], test)
    from lux.interestingness.interestingness import interestingness

    smaller_diff_score = interestingness(vis, test)
    bigger_diff_score = interestingness(vis2, test)
    assert np.isclose(smaller_diff_score, 0.19, rtol=0.1)
    assert np.isclose(bigger_diff_score, 0.62, rtol=0.1)
    assert smaller_diff_score < bigger_diff_score
