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
from lux.executor.PandasExecutor import PandasExecutor
from lux.vis.Vis import Vis
from lux.vis.VisList import VisList


def test_lazy_execution(global_var):
    df = pytest.car_df
    intent = [
        lux.Clause(attribute="Horsepower", aggregation="mean"),
        lux.Clause(attribute="Origin"),
    ]
    vis = Vis(intent)
    # Check data field in vis is empty before calling executor
    assert vis.data is None
    PandasExecutor.execute([vis], df)
    assert type(vis.data) == lux.core.frame.LuxDataFrame


def test_selection(global_var):
    df = pytest.car_df
    # change pandas dtype for the column "Year" to datetype
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    intent = [
        lux.Clause(attribute=["Horsepower", "Weight", "Acceleration"]),
        lux.Clause(attribute="Year"),
    ]
    vislist = VisList(intent, df)
    assert all([type(vis.data) == lux.core.frame.LuxDataFrame for vis in vislist])
    assert all(vislist[2].data.columns == ["Year", "Acceleration"])


def test_aggregation(global_var):
    df = pytest.car_df
    intent = [
        lux.Clause(attribute="Horsepower", aggregation="mean"),
        lux.Clause(attribute="Origin"),
    ]
    vis = Vis(intent, df)
    result_df = vis.data
    assert int(result_df[result_df["Origin"] == "USA"]["Horsepower"]) == 119

    intent = [
        lux.Clause(attribute="Horsepower", aggregation="sum"),
        lux.Clause(attribute="Origin"),
    ]
    vis = Vis(intent, df)
    result_df = vis.data
    assert int(result_df[result_df["Origin"] == "Japan"]["Horsepower"]) == 6307

    intent = [
        lux.Clause(attribute="Horsepower", aggregation="max"),
        lux.Clause(attribute="Origin"),
    ]
    vis = Vis(intent, df)
    result_df = vis.data
    assert int(result_df[result_df["Origin"] == "Europe"]["Horsepower"]) == 133


def test_colored_bar_chart(global_var):
    from lux.vis.Vis import Vis
    from lux.vis.Vis import Clause

    df = pytest.car_df

    x_clause = Clause(attribute="MilesPerGal", channel="x")
    y_clause = Clause(attribute="Origin", channel="y")
    color_clause = Clause(attribute="Cylinders", channel="color")

    new_vis = Vis([x_clause, y_clause, color_clause], df)
    # make sure dimention of the data is correct
    color_cardinality = len(df.unique_values["Cylinders"])
    group_by_cardinality = len(df.unique_values["Origin"])
    assert len(new_vis.data.columns) == 3
    # Not color_cardinality*group_by_cardinality since some combinations have 0 values
    assert len(new_vis.data) == 15 > group_by_cardinality < color_cardinality * group_by_cardinality


def test_colored_line_chart(global_var):
    from lux.vis.Vis import Vis
    from lux.vis.Vis import Clause

    df = pytest.car_df
    # change pandas dtype for the column "Year" to datetype
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")

    x_clause = Clause(attribute="Year", channel="x")
    y_clause = Clause(attribute="MilesPerGal", channel="y")
    color_clause = Clause(attribute="Cylinders", channel="color")

    new_vis = Vis([x_clause, y_clause, color_clause], df)

    # make sure dimention of the data is correct
    color_cardinality = len(df.unique_values["Cylinders"])
    group_by_cardinality = len(df.unique_values["Year"])
    assert len(new_vis.data.columns) == 3
    # Not color_cardinality*group_by_cardinality since some combinations have 0 values
    assert len(new_vis.data) == 60 > group_by_cardinality < color_cardinality * group_by_cardinality


def test_filter(global_var):
    df = pytest.car_df
    # change pandas dtype for the column "Year" to datetype
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    intent = [
        lux.Clause(attribute="Horsepower"),
        lux.Clause(attribute="Year"),
        lux.Clause(attribute="Origin", filter_op="=", value="USA"),
    ]
    vis = Vis(intent, df)
    vis._vis_data = df
    PandasExecutor.execute_filter(vis)
    assert len(vis.data) == len(df[df["Origin"] == "USA"])


def test_inequalityfilter(global_var):
    df = pytest.car_df
    vis = Vis(
        [
            lux.Clause(attribute="Horsepower", filter_op=">", value=50),
            lux.Clause(attribute="MilesPerGal"),
        ]
    )
    vis._vis_data = df
    PandasExecutor.execute_filter(vis)
    assert len(df) > len(vis.data)
    assert len(vis.data) == 386

    intent = [
        lux.Clause(attribute="Horsepower", filter_op="<=", value=100),
        lux.Clause(attribute="MilesPerGal"),
    ]
    vis = Vis(intent, df)
    vis._vis_data = df
    PandasExecutor.execute_filter(vis)
    assert len(vis.data) == len(df[df["Horsepower"] <= 100]) == 242

    # Test end-to-end
    PandasExecutor.execute([vis], df)
    Nbins = list(filter(lambda x: x.bin_size != 0, vis._inferred_intent))[0].bin_size
    assert len(vis.data) == Nbins


def test_binning(global_var):
    df = pytest.car_df
    vis = Vis([lux.Clause(attribute="Horsepower")], df)
    nbins = list(filter(lambda x: x.bin_size != 0, vis._inferred_intent))[0].bin_size
    assert len(vis.data) == nbins


def test_record(global_var):
    df = pytest.car_df
    vis = Vis([lux.Clause(attribute="Cylinders")], df)
    assert len(vis.data) == len(df["Cylinders"].unique())


def test_filter_aggregation_fillzero_aligned(global_var):
    df = pytest.car_df
    intent = [
        lux.Clause(attribute="Cylinders"),
        lux.Clause(attribute="MilesPerGal"),
        lux.Clause("Origin=Japan"),
    ]
    vis = Vis(intent, df)
    result = vis.data
    externalValidation = df[df["Origin"] == "Japan"].groupby("Cylinders").mean()["MilesPerGal"]
    assert result[result["Cylinders"] == 5]["MilesPerGal"].values[0] == 0
    assert result[result["Cylinders"] == 8]["MilesPerGal"].values[0] == 0
    assert result[result["Cylinders"] == 3]["MilesPerGal"].values[0] == externalValidation[3]
    assert result[result["Cylinders"] == 4]["MilesPerGal"].values[0] == externalValidation[4]
    assert result[result["Cylinders"] == 6]["MilesPerGal"].values[0] == externalValidation[6]


def test_exclude_attribute(global_var):
    df = pytest.car_df
    intent = [lux.Clause("?", exclude=["Name", "Year"]), lux.Clause("Horsepower")]
    vislist = VisList(intent, df)
    for vis in vislist:
        assert vis.get_attr_by_channel("x")[0].attribute != "Year"
        assert vis.get_attr_by_channel("x")[0].attribute != "Name"
        assert vis.get_attr_by_channel("y")[0].attribute != "Year"
        assert vis.get_attr_by_channel("y")[0].attribute != "Year"
