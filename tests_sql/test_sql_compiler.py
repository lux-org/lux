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


def test_underspecified_no_vis(global_var, test_recs):
    no_vis_actions = ["Correlation", "Distribution", "Occurrence", "Temporal"]
    sql_df = lux.LuxSQLTable(table_name="cars")

    test_recs(sql_df, no_vis_actions)
    assert len(sql_df.current_vis) == 0

    # test only one filter context case.
    sql_df.set_intent([lux.Clause(attribute="origin", filter_op="=", value="USA")])
    test_recs(sql_df, no_vis_actions)
    assert len(sql_df.current_vis) == 0


def test_underspecified_single_vis(global_var, test_recs):
    one_vis_actions = ["Enhance", "Filter", "Generalize"]
    lux.config.heatmap = False
    sql_df = lux.LuxSQLTable(table_name="cars")
    sql_df.set_intent([lux.Clause(attribute="milespergal"), lux.Clause(attribute="weight")])
    test_recs(sql_df, one_vis_actions)
    assert len(sql_df.current_vis) == 1
    # assert sql_df.current_vis[0].mark == "scatter"
    for attr in sql_df.current_vis[0]._inferred_intent:
        assert attr.data_model == "measure"
    for attr in sql_df.current_vis[0]._inferred_intent:
        assert attr.data_type == "quantitative"


def test_set_intent_as_vis(global_var, test_recs):
    sql_df = lux.LuxSQLTable(table_name="cars")
    sql_df._repr_html_()
    vis = sql_df.recommendation["Correlation"][0]
    sql_df.intent = vis
    sql_df._repr_html_()
    test_recs(sql_df, ["Enhance", "Filter", "Generalize"])


@pytest.fixture
def test_recs():
    def test_recs_function(df, actions):
        df._ipython_display_()
        assert len(df.recommendation) > 0
        recKeys = list(df.recommendation.keys())
        list_equal(recKeys, actions)

    return test_recs_function


def test_parse(global_var):
    sql_df = lux.LuxSQLTable(table_name="cars")
    vlst = VisList([lux.Clause("origin=?"), lux.Clause(attribute="milespergal")], sql_df)
    assert len(vlst) == 3

    sql_df = lux.LuxSQLTable(table_name="cars")
    vlst = VisList([lux.Clause("origin=?"), lux.Clause("milespergal")], sql_df)
    assert len(vlst) == 3


def test_underspecified_vis_collection_zval(global_var):
    sql_df = lux.LuxSQLTable(table_name="cars")
    vlst = VisList(
        [
            lux.Clause(attribute="origin", filter_op="=", value="?"),
            lux.Clause(attribute="milespergal"),
        ],
        sql_df,
    )
    assert len(vlst) == 3


def test_sort_bar(global_var):
    sql_df = lux.LuxSQLTable(table_name="cars")
    vis = Vis(
        [
            lux.Clause(attribute="acceleration", data_model="measure", data_type="quantitative"),
            lux.Clause(attribute="origin", data_model="dimension", data_type="nominal"),
        ],
        sql_df,
    )
    assert vis.mark == "bar"
    assert vis._inferred_intent[1].sort == ""

    sql_df = lux.LuxSQLTable(table_name="cars")
    vis = Vis(
        [
            lux.Clause(attribute="acceleration", data_model="measure", data_type="quantitative"),
            lux.Clause(attribute="name", data_model="dimension", data_type="nominal"),
        ],
        sql_df,
    )
    assert vis.mark == "bar"
    assert vis._inferred_intent[1].sort == "ascending"


def test_specified_vis_collection(global_var):
    sql_df = lux.LuxSQLTable(table_name="cars")

    vlst = VisList(
        [
            lux.Clause(attribute="horsepower"),
            lux.Clause(attribute="brand"),
            lux.Clause(attribute="origin", value=["Japan", "USA"]),
        ],
        sql_df,
    )
    assert len(vlst) == 2

    vlst = VisList(
        [
            lux.Clause(attribute=["horsepower", "weight"]),
            lux.Clause(attribute="brand"),
            lux.Clause(attribute="origin", value=["Japan", "USA"]),
        ],
        sql_df,
    )
    assert len(vlst) == 4

    # test if z axis has been filtered correctly
    chart_titles = [vis.title for vis in vlst]
    assert "origin = USA" and "origin = Japan" in chart_titles
    assert "origin = Europe" not in chart_titles


def test_specified_channel_enforced_vis_collection(global_var):
    sql_df = lux.LuxSQLTable(table_name="cars")

    visList = VisList(
        [lux.Clause(attribute="?"), lux.Clause(attribute="milespergal", channel="x")],
        sql_df,
    )
    for vis in visList:
        check_attribute_on_channel(vis, "milespergal", "x")


def test_autoencoding_scatter(global_var):
    sql_df = lux.LuxSQLTable(table_name="cars")

    vis = Vis([lux.Clause(attribute="milespergal"), lux.Clause(attribute="weight")], df)
    check_attribute_on_channel(vis, "milespergal", "x")
    check_attribute_on_channel(vis, "weight", "y")

    # Partial channel specified
    vis = Vis(
        [
            lux.Clause(attribute="milespergal", channel="y"),
            lux.Clause(attribute="weight"),
        ],
        sql_df,
    )
    check_attribute_on_channel(vis, "milespergal", "y")
    check_attribute_on_channel(vis, "weight", "x")

    # Full channel specified
    vis = Vis(
        [
            lux.Clause(attribute="milespergal", channel="y"),
            lux.Clause(attribute="weight", channel="x"),
        ],
        sql_df,
    )
    check_attribute_on_channel(vis, "milespergal", "y")
    check_attribute_on_channel(vis, "weight", "x")
    # Duplicate channel specified
    with pytest.raises(ValueError):
        # Should throw error because there should not be columns with the same channel specified
        sql_df.set_intent(
            [
                lux.Clause(attribute="milespergal", channel="x"),
                lux.Clause(attribute="weight", channel="x"),
            ]
        )
    df.clear_intent()

    sql_df = lux.LuxSQLTable(table_name="cars")
    visList = VisList(
        [lux.Clause(attribute="?"), lux.Clause(attribute="milespergal", channel="x")],
        sql_df,
    )
    for vis in visList:
        check_attribute_on_channel(vis, "milespergal", "x")


def test_autoencoding_scatter():
    sql_df = lux.LuxSQLTable(table_name="cars")

    vis = Vis([lux.Clause(attribute="milespergal"), lux.Clause(attribute="weight")], sql_df)
    check_attribute_on_channel(vis, "milespergal", "x")
    check_attribute_on_channel(vis, "weight", "y")

    # Partial channel specified
    vis = Vis(
        [
            lux.Clause(attribute="milespergal", channel="y"),
            lux.Clause(attribute="weight"),
        ],
        sql_df,
    )
    check_attribute_on_channel(vis, "milespergal", "y")
    check_attribute_on_channel(vis, "weight", "x")

    # Full channel specified
    vis = Vis(
        [
            lux.Clause(attribute="milespergal", channel="y"),
            lux.Clause(attribute="weight", channel="x"),
        ],
        sql_df,
    )
    check_attribute_on_channel(vis, "milespergal", "y")
    check_attribute_on_channel(vis, "weight", "x")
    # Duplicate channel specified
    with pytest.raises(ValueError):
        # Should throw error because there should not be columns with the same channel specified
        sql_df.set_intent(
            [
                lux.Clause(attribute="milespergal", channel="x"),
                lux.Clause(attribute="weight", channel="x"),
            ]
        )

    # test for sql executor
    sql_df = lux.LuxSQLTable(table_name="cars")
    vis = Vis([lux.Clause(attribute="milespergal"), lux.Clause(attribute="weight")], sql_df)
    check_attribute_on_channel(vis, "milespergal", "x")
    check_attribute_on_channel(vis, "weight", "y")

    # Partial channel specified
    vis = Vis(
        [
            lux.Clause(attribute="milespergal", channel="y"),
            lux.Clause(attribute="weight"),
        ],
        sql_df,
    )
    check_attribute_on_channel(vis, "milespergal", "y")
    check_attribute_on_channel(vis, "weight", "x")

    # Full channel specified
    vis = Vis(
        [
            lux.Clause(attribute="milespergal", channel="y"),
            lux.Clause(attribute="weight", channel="x"),
        ],
        sql_df,
    )
    check_attribute_on_channel(vis, "milespergal", "y")
    check_attribute_on_channel(vis, "weight", "x")
    # Duplicate channel specified
    with pytest.raises(ValueError):
        # Should throw error because there should not be columns with the same channel specified
        sql_df.set_intent(
            [
                lux.Clause(attribute="milespergal", channel="x"),
                lux.Clause(attribute="weight", channel="x"),
            ]
        )


def test_autoencoding_histogram(global_var):
    # No channel specified
    # test for sql executor
    sql_df = lux.LuxSQLTable(table_name="cars")
    vis = Vis([lux.Clause(attribute="milespergal", channel="y")], sql_df)
    check_attribute_on_channel(vis, "milespergal", "y")

    vis = Vis([lux.Clause(attribute="milespergal", channel="x")], sql_df)
    assert vis.get_attr_by_channel("x")[0].attribute == "milespergal"
    assert vis.get_attr_by_channel("y")[0].attribute == "Record"


def test_autoencoding_line_chart(global_var):
    # test for sql executor
    sql_df = lux.LuxSQLTable(table_name="cars")
    vis = Vis([lux.Clause(attribute="year"), lux.Clause(attribute="acceleration")], sql_df)
    check_attribute_on_channel(vis, "year", "x")
    check_attribute_on_channel(vis, "acceleration", "y")

    # Partial channel specified
    vis = Vis(
        [
            lux.Clause(attribute="year", channel="y"),
            lux.Clause(attribute="acceleration"),
        ],
        sql_df,
    )
    check_attribute_on_channel(vis, "year", "y")
    check_attribute_on_channel(vis, "acceleration", "x")

    # Full channel specified
    vis = Vis(
        [
            lux.Clause(attribute="year", channel="y"),
            lux.Clause(attribute="acceleration", channel="x"),
        ],
        sql_df,
    )
    check_attribute_on_channel(vis, "year", "y")
    check_attribute_on_channel(vis, "acceleration", "x")

    with pytest.raises(ValueError):
        # Should throw error because there should not be columns with the same channel specified
        sql_df.set_intent(
            [
                lux.Clause(attribute="year", channel="x"),
                lux.Clause(attribute="acceleration", channel="x"),
            ]
        )


def test_autoencoding_color_line_chart(global_var):
    # test for sql executor
    sql_df = lux.LuxSQLTable(table_name="cars")
    intent = [
        lux.Clause(attribute="year"),
        lux.Clause(attribute="acceleration"),
        lux.Clause(attribute="origin"),
    ]
    vis = Vis(intent, sql_df)
    check_attribute_on_channel(vis, "year", "x")
    check_attribute_on_channel(vis, "acceleration", "y")
    check_attribute_on_channel(vis, "origin", "color")


# def test_autoencoding_color_scatter_chart(global_var):
#     # test for sql executor
#     sql_df = lux.LuxSQLTable(table_name="cars")
#     vis = Vis(
#         [
#             lux.Clause(attribute="horsepower"),
#             lux.Clause(attribute="acceleration"),
#             lux.Clause(attribute="origin"),
#         ],
#         sql_df,
#     )
#     check_attribute_on_channel(vis, "origin", "color")

#     vis = Vis(
#         [
#             lux.Clause(attribute="horsepower"),
#             lux.Clause(attribute="acceleration", channel="color"),
#             lux.Clause(attribute="origin"),
#         ],
#         sql_df,
#     )
#     check_attribute_on_channel(vis, "acceleration", "color")


def test_populate_options(global_var):
    from lux.processor.Compiler import Compiler

    # test for sql executor
    sql_df = lux.LuxSQLTable(table_name="cars")
    sql_df.set_intent([lux.Clause(attribute="?"), lux.Clause(attribute="milespergal")])
    col_set = set()
    for specOptions in Compiler.populate_wildcard_options(sql_df._intent, sql_df)["attributes"]:
        for clause in specOptions:
            col_set.add(clause.attribute)
    assert list_equal(list(col_set), list(sql_df.columns))

    sql_df.set_intent(
        [
            lux.Clause(attribute="?", data_model="measure"),
            lux.Clause(attribute="milespergal"),
        ]
    )
    sql_df._repr_html_()
    col_set = set()
    for specOptions in Compiler.populate_wildcard_options(sql_df._intent, sql_df)["attributes"]:
        for clause in specOptions:
            col_set.add(clause.attribute)
    assert list_equal(
        list(col_set),
        ["acceleration", "weight", "horsepower", "milespergal", "displacement"],
    )


def test_remove_all_invalid(global_var):
    # test for sql executor
    sql_df = lux.LuxSQLTable(table_name="cars")
    # with pytest.warns(UserWarning,match="duplicate attribute specified in the intent"):
    sql_df.set_intent(
        [
            lux.Clause(attribute="origin", filter_op="=", value="USA"),
            lux.Clause(attribute="origin"),
        ]
    )
    sql_df._repr_html_()
    assert len(sql_df.current_vis) == 0


def list_equal(l1, l2):
    l1.sort()
    l2.sort()
    return l1 == l2


def check_attribute_on_channel(vis, attr_name, channelName):
    assert vis.get_attr_by_channel(channelName)[0].attribute == attr_name
