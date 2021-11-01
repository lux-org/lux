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
from lux.vis.Vis import Vis


def test_metadata_subsequent_display(global_var):
    df = pytest.car_df
    df._ipython_display_()
    assert df._metadata_fresh == True, "Failed to maintain metadata after display df"
    df._ipython_display_()
    assert df._metadata_fresh == True, "Failed to maintain metadata after display df"


def test_metadata_subsequent_vis(global_var):
    df = pytest.car_df
    df._ipython_display_()
    assert df._metadata_fresh == True, "Failed to maintain metadata after display df"
    vis = Vis(["Acceleration", "Horsepower"], df)
    assert df._metadata_fresh == True, "Failed to maintain metadata after display df"


def test_metadata_inplace_operation(global_var):
    df = pytest.car_df
    df._ipython_display_()
    assert df._metadata_fresh == True, "Failed to maintain metadata after display df"
    df.dropna(inplace=True)
    assert df._metadata_fresh == False, "Failed to expire metadata after in-place Pandas operation"


def test_metadata_new_df_operation(global_var):
    df = pytest.car_df
    df._ipython_display_()
    assert df._metadata_fresh == True, "Failed to maintain metadata after display df"
    df[["MilesPerGal", "Acceleration"]]
    assert df._metadata_fresh == True, "Failed to maintain metadata after display df"
    df2 = df[["MilesPerGal", "Acceleration"]]
    assert not hasattr(df2, "_metadata_fresh")


# Test fails in version 1.3.0+
# def test_metadata_column_group_reset_df(global_var):
#     df = pd.read_csv("lux/data/car.csv")
#     assert not hasattr(df, "_metadata_fresh")
#     df["Year"] = pd.to_datetime(df["Year"], format="%Y")
#     assert hasattr(df, "_metadata_fresh")
#     result = df.groupby("Cylinders").mean()
#     assert not hasattr(result, "_metadata_fresh")
#     # Note that this should trigger two compute metadata (one for df, and one for an intermediate df.reset_index used to feed inside created Vis)
#     result._ipython_display_()
#     assert result._metadata_fresh == True, "Failed to maintain metadata after display df"

#     colgroup_recs = result.recommendation["Column Groups"]
#     assert len(colgroup_recs) == 5
#     for rec in colgroup_recs:
#         assert rec.mark == "bar", "Column Group not displaying bar charts"


def test_recs_inplace_operation(global_var):
    df = pytest.college_df
    df._ipython_display_()
    assert df._recs_fresh == True, "Failed to maintain recommendation after display df"
    assert len(df.recommendation["Occurrence"]) == 6
    df.drop(columns=["Name"], inplace=True)
    assert "Name" not in df.columns, "Failed to perform `drop` operation in-place"
    assert df._recs_fresh == False, "Failed to maintain recommendation after in-place Pandas operation"
    df._ipython_display_()
    assert len(df.recommendation["Occurrence"]) == 5
    assert df._recs_fresh == True, "Failed to maintain recommendation after display df"


def test_intent_cleared_after_vis_data():
    df = pd.read_csv(
        "https://github.com/lux-org/lux-datasets/blob/master/data/real_estate_tutorial.csv?raw=true"
    )
    df["Month"] = pd.to_datetime(df["Month"], format="%m")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df.intent = [
        lux.Clause("Year"),
        lux.Clause("PctForeclosured"),
        lux.Clause("City=Crofton"),
    ]
    df._ipython_display_()

    vis = df.recommendation["Similarity"][0]
    vis.data._ipython_display_()
    all_column_vis = vis.data.current_vis[0]
    assert all_column_vis.get_attr_by_channel("x")[0].attribute == "Year"
    assert all_column_vis.get_attr_by_channel("y")[0].attribute == "PctForeclosured"
