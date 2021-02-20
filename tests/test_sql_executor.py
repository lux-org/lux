#  Copyright 2019-2020 The Lux Authors.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
# 	  http://www.apache.org/licenses/LICENSE-2.0

#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from .context import lux
import pytest
import pandas as pd
from lux.executor.SQLExecutor import SQLExecutor
from lux.vis.Vis import Vis
from lux.vis.VisList import VisList
import psycopg2


def test_lazy_execution():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxDataFrame()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("cars")

    intent = [
        lux.Clause(attribute="horsepower", aggregation="mean"),
        lux.Clause(attribute="origin"),
    ]
    vis = Vis(intent)
    # Check data field in vis is empty before calling executor
    assert vis.data is None
    SQLExecutor.execute([vis], sql_df)
    assert type(vis.data) == lux.core.frame.LuxDataFrame


def test_selection():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxDataFrame()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("cars")

    intent = [
        lux.Clause(attribute=["horsepower", "weight", "acceleration"]),
        lux.Clause(attribute="year"),
    ]
    vislist = VisList(intent, sql_df)
    assert all([type(vis.data) == lux.core.frame.LuxDataFrame for vis in vislist])
    assert all(vislist[2].data.columns == ["year", "acceleration"])


def test_aggregation():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxDataFrame()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("cars")

    intent = [
        lux.Clause(attribute="horsepower", aggregation="mean"),
        lux.Clause(attribute="origin"),
    ]
    vis = Vis(intent, sql_df)
    result_df = vis.data
    assert int(result_df[result_df["origin"] == "USA"]["horsepower"]) == 119

    intent = [
        lux.Clause(attribute="horsepower", aggregation="sum"),
        lux.Clause(attribute="origin"),
    ]
    vis = Vis(intent, sql_df)
    result_df = vis.data
    assert int(result_df[result_df["origin"] == "Japan"]["horsepower"]) == 6307

    intent = [
        lux.Clause(attribute="horsepower", aggregation="max"),
        lux.Clause(attribute="origin"),
    ]
    vis = Vis(intent, sql_df)
    result_df = vis.data
    assert int(result_df[result_df["origin"] == "Europe"]["horsepower"]) == 133


def test_colored_bar_chart():
    from lux.vis.Vis import Vis
    from lux.vis.Vis import Clause

    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxDataFrame()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("cars")

    x_clause = Clause(attribute="milespergal", channel="x")
    y_clause = Clause(attribute="origin", channel="y")
    color_clause = Clause(attribute="cylinders", channel="color")

    new_vis = Vis([x_clause, y_clause, color_clause], sql_df)
    # make sure dimention of the data is correct
    color_cardinality = len(sql_df.unique_values["cylinders"])
    group_by_cardinality = len(sql_df.unique_values["origin"])
    assert len(new_vis.data.columns) == 3
    assert (
        len(new_vis.data) == 15 > group_by_cardinality < color_cardinality * group_by_cardinality
    )  # Not color_cardinality*group_by_cardinality since some combinations have 0 values


def test_colored_line_chart():
    from lux.vis.Vis import Vis
    from lux.vis.Vis import Clause

    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxDataFrame()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("cars")

    x_clause = Clause(attribute="year", channel="x")
    y_clause = Clause(attribute="milespergal", channel="y")
    color_clause = Clause(attribute="cylinders", channel="color")

    new_vis = Vis([x_clause, y_clause, color_clause], sql_df)

    # make sure dimention of the data is correct
    color_cardinality = len(sql_df.unique_values["cylinders"])
    group_by_cardinality = len(sql_df.unique_values["year"])
    assert len(new_vis.data.columns) == 3
    assert (
        len(new_vis.data) == 60 > group_by_cardinality < color_cardinality * group_by_cardinality
    )  # Not color_cardinality*group_by_cardinality since some combinations have 0 values


def test_filter():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxDataFrame()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("cars")

    intent = [
        lux.Clause(attribute="horsepower"),
        lux.Clause(attribute="year"),
        lux.Clause(attribute="origin", filter_op="=", value="USA"),
    ]
    vis = Vis(intent, sql_df)
    vis._vis_data = sql_df
    filter_output = SQLExecutor.execute_filter(vis)
    assert (
        filter_output[0]
        == 'WHERE "origin" = \'USA\''
    )
    assert filter_output[1] == ["origin"]


def test_inequalityfilter():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxDataFrame()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("cars")

    vis = Vis(
        [
            lux.Clause(attribute="horsepower", filter_op=">", value=50),
            lux.Clause(attribute="milespergal"),
        ]
    )
    vis._vis_data = sql_df
    filter_output = SQLExecutor.execute_filter(vis)
    assert filter_output[0] == 'WHERE "horsepower" > \'50\''
    assert filter_output[1] == ["horsepower"]

    intent = [
        lux.Clause(attribute="horsepower", filter_op="<=", value=100),
        lux.Clause(attribute="milespergal"),
    ]
    vis = Vis(intent, sql_df)
    vis._vis_data = sql_df
    filter_output = SQLExecutor.execute_filter(vis)
    assert filter_output[0] == 'WHERE "horsepower" <= \'100\''
    assert filter_output[1] == ["horsepower"]


def test_binning():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxDataFrame()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("cars")

    vis = Vis([lux.Clause(attribute="horsepower")], sql_df)
    nbins = list(filter(lambda x: x.bin_size != 0, vis._inferred_intent))[0].bin_size
    assert len(vis.data) == nbins


def test_record():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxDataFrame()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("cars")

    vis = Vis([lux.Clause(attribute="cylinders")], sql_df)
    assert len(vis.data) == len(sql_df.unique_values["cylinders"])


def test_filter_aggregation_fillzero_aligned():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxDataFrame()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("cars")

    intent = [
        lux.Clause(attribute="cylinders"),
        lux.Clause(attribute="milespergal"),
        lux.Clause("origin=Japan"),
    ]
    vis = Vis(intent, sql_df)
    result = vis.data
    assert result[result["cylinders"] == 5]["milespergal"].values[0] == 0
    assert result[result["cylinders"] == 8]["milespergal"].values[0] == 0


def test_exclude_attribute():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxDataFrame()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("cars")

    intent = [lux.Clause("?", exclude=["name", "year"]), lux.Clause("horsepower")]
    vislist = VisList(intent, sql_df)
    for vis in vislist:
        assert vis.get_attr_by_channel("x")[0].attribute != "year"
        assert vis.get_attr_by_channel("x")[0].attribute != "name"
        assert vis.get_attr_by_channel("y")[0].attribute != "year"
        assert vis.get_attr_by_channel("y")[0].attribute != "year"
