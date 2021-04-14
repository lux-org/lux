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
from lux.vis.VisList import VisList
import psycopg2


def test_underspecified_no_vis(global_var, test_recs):
    no_vis_actions = ["Correlation", "Distribution", "Occurrence", "Temporal"]
    df = pytest.car_df
    test_recs(df, no_vis_actions)
    assert df.current_vis is None or len(df.current_vis) == 0

    # test only one filter context case.
    df.set_intent([lux.Clause(attribute="Origin", filter_op="=", value="USA")])
    test_recs(df, no_vis_actions)
    assert len(df.current_vis) == 0
    df.clear_intent()


def test_underspecified_single_vis(global_var, test_recs):
    one_vis_actions = ["Enhance", "Filter", "Generalize"]
    df = pytest.car_df
    df.set_intent([lux.Clause(attribute="MilesPerGal"), lux.Clause(attribute="Weight")])
    test_recs(df, one_vis_actions)
    assert len(df.current_vis) == 1
    assert df.current_vis[0].mark == "scatter"
    for attr in df.current_vis[0]._inferred_intent:
        assert attr.data_model == "measure"
    for attr in df.current_vis[0]._inferred_intent:
        assert attr.data_type == "quantitative"
    df.clear_intent()


# def test_underspecified_vis_collection(test_recs):
# 	multiple_vis_actions = ["Current viss"]

# 	df = pd.read_csv("lux/data/car.csv")
# 	df["Year"] = pd.to_datetime(df["Year"], format='%Y') # change pandas dtype for the column "Year" to datetype

# 	df.set_intent([lux.Clause(attribute = ["Horsepower", "Weight", "Acceleration"]), lux.Clause(attribute ="Year", channel="x")])
# 	assert len(df.current_vis) == 3
# 	assert df.current_vis[0].mark == "line"
# 	for vlist in df.current_vis:
# 		assert (vlist.get_attr_by_channel("x")[0].attribute == "Year")
# 	test_recs(df, multiple_vis_actions)

# 	df.set_intent([lux.Clause(attribute ="?"), lux.Clause(attribute ="Year", channel="x")])
# 	assert len(df.current_vis) == len(list(df.columns)) - 1 # we remove year by year so its 8 vis instead of 9
# 	for vlist in df.current_vis:
# 		assert (vlist.get_attr_by_channel("x")[0].attribute == "Year")
# 	test_recs(df, multiple_vis_actions)

# 	df.set_intent([lux.Clause(attribute ="?", data_type="quantitative"), lux.Clause(attribute ="Year")])
# 	assert len(df.current_vis) == len([vis.get_attr_by_data_type("quantitative") for vis in df.current_vis]) # should be 5
# 	test_recs(df, multiple_vis_actions)

# 	df.set_intent([lux.Clause(attribute ="?", data_model="measure"), lux.Clause(attribute="MilesPerGal", channel="y")])
# 	for vlist in df.current_vis:
# 		print (vlist.get_attr_by_channel("y")[0].attribute == "MilesPerGal")
# 	test_recs(df, multiple_vis_actions)

# 	df.set_intent([lux.Clause(attribute ="?", data_model="measure"), lux.Clause(attribute ="?", data_model="measure")])
# 	assert len(df.current_vis) == len([vis.get_attr_by_data_model("measure") for vis in df.current_vis]) #should be 25
# 	test_recs(df, multiple_vis_actions)


def test_set_intent_as_vis(global_var, test_recs):
    lux.config.set_executor_type("Pandas")
    df = pytest.car_df
    df._ipython_display_()
    vis = df.recommendation["Correlation"][0]
    df.intent = vis
    df._ipython_display_()
    test_recs(df, ["Enhance", "Filter", "Generalize"])


@pytest.fixture
def test_recs():
    def test_recs_function(df, actions):
        df._ipython_display_()
        assert len(df.recommendation) > 0
        recKeys = list(df.recommendation.keys())
        list_equal(recKeys, actions)

    return test_recs_function


def test_parse(global_var):
    lux.config.set_executor_type("Pandas")
    df = pytest.car_df
    vlst = VisList([lux.Clause("Origin=?"), lux.Clause(attribute="MilesPerGal")], df)
    assert len(vlst) == 3

    df = pytest.car_df
    vlst = VisList([lux.Clause("Origin=?"), lux.Clause("MilesPerGal")], df)
    assert len(vlst) == 3

    df = pd.read_csv("lux/data/car.csv")
    vlst = VisList([lux.Clause("Origin=?"), lux.Clause("MilesPerGal")], df)
    assert len(vlst) == 3


def test_underspecified_vis_collection_zval(global_var):
    lux.config.set_executor_type("Pandas")
    # check if the number of charts is correct
    df = pytest.car_df
    vlst = VisList(
        [
            lux.Clause(attribute="Origin", filter_op="=", value="?"),
            lux.Clause(attribute="MilesPerGal"),
        ],
        df,
    )
    assert len(vlst) == 3

    # does not work
    # df = pd.read_csv("lux/data/car.csv")
    # vlst = VisList([lux.Clause(attribute = ["Origin","Cylinders"], filter_op="=",value="?"),lux.Clause(attribute = ["Horsepower"]),lux.Clause(attribute = "Weight")],df)
    # assert len(vlst) == 8


def test_sort_bar(global_var):
    from lux.processor.Compiler import Compiler
    from lux.vis.Vis import Vis

    lux.config.set_executor_type("Pandas")
    df = pytest.car_df
    vis = Vis(
        [
            lux.Clause(attribute="Acceleration", data_model="measure", data_type="quantitative"),
            lux.Clause(attribute="Origin", data_model="dimension", data_type="nominal"),
        ],
        df,
    )
    assert vis.mark == "bar"
    assert vis._inferred_intent[1].sort == ""

    df = pytest.car_df
    vis = Vis(
        [
            lux.Clause(attribute="Acceleration", data_model="measure", data_type="quantitative"),
            lux.Clause(attribute="Name", data_model="dimension", data_type="nominal"),
        ],
        df,
    )
    assert vis.mark == "bar"
    assert vis._inferred_intent[1].sort == "ascending"


def test_specified_vis_collection(global_var):
    lux.config.set_executor_type("Pandas")
    df = pytest.car_df
    # change pandas dtype for the column "Year" to datetype
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")

    vlst = VisList(
        [
            lux.Clause(attribute="Horsepower"),
            lux.Clause(attribute="Brand"),
            lux.Clause(attribute="Origin", value=["Japan", "USA"]),
        ],
        df,
    )
    assert len(vlst) == 2

    vlst = VisList(
        [
            lux.Clause(attribute=["Horsepower", "Weight"]),
            lux.Clause(attribute="Brand"),
            lux.Clause(attribute="Origin", value=["Japan", "USA"]),
        ],
        df,
    )
    assert len(vlst) == 4

    # test if z axis has been filtered correctly
    chart_titles = [vis.title for vis in vlst]
    assert "Origin = USA" and "Origin = Japan" in chart_titles
    assert "Origin = Europe" not in chart_titles


def test_specified_channel_enforced_vis_collection(global_var):
    lux.config.set_executor_type("Pandas")
    df = pytest.car_df
    # change pandas dtype for the column "Year" to datetype
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    visList = VisList(
        [lux.Clause(attribute="?"), lux.Clause(attribute="MilesPerGal", channel="x")],
        df,
    )
    for vis in visList:
        check_attribute_on_channel(vis, "MilesPerGal", "x")


def test_autoencoding_scatter(global_var):
    lux.config.set_executor_type("Pandas")
    # No channel specified
    df = pytest.car_df
    # change pandas dtype for the column "Year" to datetype
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    vis = Vis([lux.Clause(attribute="MilesPerGal"), lux.Clause(attribute="Weight")], df)
    check_attribute_on_channel(vis, "MilesPerGal", "x")
    check_attribute_on_channel(vis, "Weight", "y")

    # Partial channel specified
    vis = Vis(
        [
            lux.Clause(attribute="MilesPerGal", channel="y"),
            lux.Clause(attribute="Weight"),
        ],
        df,
    )
    check_attribute_on_channel(vis, "MilesPerGal", "y")
    check_attribute_on_channel(vis, "Weight", "x")

    # Full channel specified
    vis = Vis(
        [
            lux.Clause(attribute="MilesPerGal", channel="y"),
            lux.Clause(attribute="Weight", channel="x"),
        ],
        df,
    )
    check_attribute_on_channel(vis, "MilesPerGal", "y")
    check_attribute_on_channel(vis, "Weight", "x")
    # Duplicate channel specified
    with pytest.raises(ValueError):
        # Should throw error because there should not be columns with the same channel specified
        df.set_intent(
            [
                lux.Clause(attribute="MilesPerGal", channel="x"),
                lux.Clause(attribute="Weight", channel="x"),
            ]
        )
    df.clear_intent()


def test_autoencoding_scatter():
    lux.config.set_executor_type("Pandas")
    # No channel specified
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(
        df["Year"], format="%Y"
    )  # change pandas dtype for the column "Year" to datetype
    vis = Vis([lux.Clause(attribute="MilesPerGal"), lux.Clause(attribute="Weight")], df)
    check_attribute_on_channel(vis, "MilesPerGal", "x")
    check_attribute_on_channel(vis, "Weight", "y")

    # Partial channel specified
    vis = Vis(
        [
            lux.Clause(attribute="MilesPerGal", channel="y"),
            lux.Clause(attribute="Weight"),
        ],
        df,
    )
    check_attribute_on_channel(vis, "MilesPerGal", "y")
    check_attribute_on_channel(vis, "Weight", "x")

    # Full channel specified
    vis = Vis(
        [
            lux.Clause(attribute="MilesPerGal", channel="y"),
            lux.Clause(attribute="Weight", channel="x"),
        ],
        df,
    )
    check_attribute_on_channel(vis, "MilesPerGal", "y")
    check_attribute_on_channel(vis, "Weight", "x")
    # Duplicate channel specified
    with pytest.raises(ValueError):
        # Should throw error because there should not be columns with the same channel specified
        df.set_intent(
            [
                lux.Clause(attribute="MilesPerGal", channel="x"),
                lux.Clause(attribute="Weight", channel="x"),
            ]
        )


def test_autoencoding_scatter():
    lux.config.set_executor_type("Pandas")
    # No channel specified
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(
        df["Year"], format="%Y"
    )  # change pandas dtype for the column "Year" to datetype
    vis = Vis([lux.Clause(attribute="MilesPerGal"), lux.Clause(attribute="Weight")], df)
    check_attribute_on_channel(vis, "MilesPerGal", "x")
    check_attribute_on_channel(vis, "Weight", "y")

    # Partial channel specified
    vis = Vis(
        [
            lux.Clause(attribute="MilesPerGal", channel="y"),
            lux.Clause(attribute="Weight"),
        ],
        df,
    )
    check_attribute_on_channel(vis, "MilesPerGal", "y")
    check_attribute_on_channel(vis, "Weight", "x")

    # Full channel specified
    vis = Vis(
        [
            lux.Clause(attribute="MilesPerGal", channel="y"),
            lux.Clause(attribute="Weight", channel="x"),
        ],
        df,
    )
    check_attribute_on_channel(vis, "MilesPerGal", "y")
    check_attribute_on_channel(vis, "Weight", "x")
    # Duplicate channel specified
    with pytest.raises(ValueError):
        # Should throw error because there should not be columns with the same channel specified
        df.set_intent(
            [
                lux.Clause(attribute="MilesPerGal", channel="x"),
                lux.Clause(attribute="Weight", channel="x"),
            ]
        )


def test_autoencoding_histogram(global_var):
    lux.config.set_executor_type("Pandas")
    # No channel specified
    df = pytest.car_df
    # change pandas dtype for the column "Year" to datetype
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    vis = Vis([lux.Clause(attribute="MilesPerGal", channel="y")], df)
    check_attribute_on_channel(vis, "MilesPerGal", "y")

    vis = Vis([lux.Clause(attribute="MilesPerGal", channel="x")], df)
    assert vis.get_attr_by_channel("x")[0].attribute == "MilesPerGal"
    assert vis.get_attr_by_channel("y")[0].attribute == "Record"


def test_autoencoding_line_chart(global_var):
    lux.config.set_executor_type("Pandas")
    df = pytest.car_df
    # change pandas dtype for the column "Year" to datetype
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    vis = Vis([lux.Clause(attribute="Year"), lux.Clause(attribute="Acceleration")], df)
    check_attribute_on_channel(vis, "Year", "x")
    check_attribute_on_channel(vis, "Acceleration", "y")

    # Partial channel specified
    vis = Vis(
        [
            lux.Clause(attribute="Year", channel="y"),
            lux.Clause(attribute="Acceleration"),
        ],
        df,
    )
    check_attribute_on_channel(vis, "Year", "y")
    check_attribute_on_channel(vis, "Acceleration", "x")

    # Full channel specified
    vis = Vis(
        [
            lux.Clause(attribute="Year", channel="y"),
            lux.Clause(attribute="Acceleration", channel="x"),
        ],
        df,
    )
    check_attribute_on_channel(vis, "Year", "y")
    check_attribute_on_channel(vis, "Acceleration", "x")

    with pytest.raises(ValueError):
        # Should throw error because there should not be columns with the same channel specified
        df.set_intent(
            [
                lux.Clause(attribute="Year", channel="x"),
                lux.Clause(attribute="Acceleration", channel="x"),
            ]
        )
    df.clear_intent()


def test_autoencoding_color_line_chart(global_var):
    lux.config.set_executor_type("Pandas")
    df = pytest.car_df
    # change pandas dtype for the column "Year" to datetype
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    intent = [
        lux.Clause(attribute="Year"),
        lux.Clause(attribute="Acceleration"),
        lux.Clause(attribute="Origin"),
    ]
    vis = Vis(intent, df)
    check_attribute_on_channel(vis, "Year", "x")
    check_attribute_on_channel(vis, "Acceleration", "y")
    check_attribute_on_channel(vis, "Origin", "color")


def test_autoencoding_color_scatter_chart(global_var):
    lux.config.set_executor_type("Pandas")
    df = pytest.car_df
    # change pandas dtype for the column "Year" to datetype
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    vis = Vis(
        [
            lux.Clause(attribute="Horsepower"),
            lux.Clause(attribute="Acceleration"),
            lux.Clause(attribute="Origin"),
        ],
        df,
    )
    check_attribute_on_channel(vis, "Origin", "color")

    vis = Vis(
        [
            lux.Clause(attribute="Horsepower"),
            lux.Clause(attribute="Acceleration", channel="color"),
            lux.Clause(attribute="Origin"),
        ],
        df,
    )
    check_attribute_on_channel(vis, "Acceleration", "color")


def test_populate_options(global_var):
    lux.config.set_executor_type("Pandas")
    from lux.processor.Compiler import Compiler

    df = pytest.car_df
    df.set_intent([lux.Clause(attribute="?"), lux.Clause(attribute="MilesPerGal")])
    col_set = set()
    for specOptions in Compiler.populate_wildcard_options(df._intent, df)["attributes"]:
        for clause in specOptions:
            col_set.add(clause.attribute)
    assert list_equal(list(col_set), list(df.columns))

    df.set_intent(
        [
            lux.Clause(attribute="?", data_model="measure"),
            lux.Clause(attribute="MilesPerGal"),
        ]
    )
    df._ipython_display_()
    col_set = set()
    for specOptions in Compiler.populate_wildcard_options(df._intent, df)["attributes"]:
        for clause in specOptions:
            col_set.add(clause.attribute)
    assert list_equal(
        list(col_set),
        ["Acceleration", "Weight", "Horsepower", "MilesPerGal", "Displacement"],
    )
    df.clear_intent()


def test_remove_all_invalid(global_var):
    lux.config.set_executor_type("Pandas")
    df = pytest.car_df
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    # with pytest.warns(UserWarning,match="duplicate attribute specified in the intent"):
    df.set_intent(
        [
            lux.Clause(attribute="Origin", filter_op="=", value="USA"),
            lux.Clause(attribute="Origin"),
        ]
    )
    df._ipython_display_()
    assert len(df.current_vis) == 0
    df.clear_intent()


def list_equal(l1, l2):
    l1.sort()
    l2.sort()
    return l1 == l2


def check_attribute_on_channel(vis, attr_name, channelName):
    assert vis.get_attr_by_channel(channelName)[0].attribute == attr_name
