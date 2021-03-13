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
    sql_df = lux.LuxSQLTable()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("car")

    intent = [
        lux.Clause(attribute="Horsepower", aggregation="mean"),
        lux.Clause(attribute="Origin"),
    ]
    vis = Vis(intent)
    # Check data field in vis is empty before calling executor
    assert vis.data is None
    SQLExecutor.execute([vis], sql_df)
    assert type(vis.data) == lux.core.frame.LuxDataFrame


def test_selection():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxSQLTable()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("car")

    intent = [
        lux.Clause(attribute=["Horsepower", "Weight", "Acceleration"]),
        lux.Clause(attribute="Year"),
    ]
    vislist = VisList(intent, sql_df)
    assert all([type(vis.data) == lux.core.frame.LuxDataFrame for vis in vislist])
    assert all(vislist[2].data.columns == ["Year", "Acceleration"])


def test_aggregation():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxSQLTable()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("car")

    intent = [
        lux.Clause(attribute="Horsepower", aggregation="mean"),
        lux.Clause(attribute="Origin"),
    ]
    vis = Vis(intent, sql_df)
    result_df = vis.data
    assert int(result_df[result_df["Origin"] == "USA"]["Horsepower"]) == 119

    intent = [
        lux.Clause(attribute="Horsepower", aggregation="sum"),
        lux.Clause(attribute="Origin"),
    ]
    vis = Vis(intent, sql_df)
    result_df = vis.data
    assert int(result_df[result_df["Origin"] == "Japan"]["Horsepower"]) == 6307

    intent = [
        lux.Clause(attribute="Horsepower", aggregation="max"),
        lux.Clause(attribute="Origin"),
    ]
    vis = Vis(intent, sql_df)
    result_df = vis.data
    assert int(result_df[result_df["Origin"] == "Europe"]["Horsepower"]) == 133


def test_colored_bar_chart():
    from lux.vis.Vis import Vis
    from lux.vis.Vis import Clause

    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxSQLTable()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("car")

    x_clause = Clause(attribute="MilesPerGal", channel="x")
    y_clause = Clause(attribute="Origin", channel="y")
    color_clause = Clause(attribute="Cylinders", channel="color")

    new_vis = Vis([x_clause, y_clause, color_clause], sql_df)
    # make sure dimention of the data is correct
    color_cardinality = len(sql_df.unique_values["Cylinders"])
    group_by_cardinality = len(sql_df.unique_values["Origin"])
    assert len(new_vis.data.columns) == 3
    assert (
        len(new_vis.data) == 15 > group_by_cardinality < color_cardinality * group_by_cardinality
    )  # Not color_cardinality*group_by_cardinality since some combinations have 0 values


def test_colored_line_chart():
    from lux.vis.Vis import Vis
    from lux.vis.Vis import Clause

    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxSQLTable()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("car")

    x_clause = Clause(attribute="Year", channel="x")
    y_clause = Clause(attribute="MilesPerGal", channel="y")
    color_clause = Clause(attribute="Cylinders", channel="color")

    new_vis = Vis([x_clause, y_clause, color_clause], sql_df)

    # make sure dimention of the data is correct
    color_cardinality = len(sql_df.unique_values["Cylinders"])
    group_by_cardinality = len(sql_df.unique_values["Year"])
    assert len(new_vis.data.columns) == 3
    assert (
        len(new_vis.data) == 60 > group_by_cardinality < color_cardinality * group_by_cardinality
    )  # Not color_cardinality*group_by_cardinality since some combinations have 0 values


def test_filter():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxSQLTable()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("car")

    intent = [
        lux.Clause(attribute="Horsepower"),
        lux.Clause(attribute="Year"),
        lux.Clause(attribute="Origin", filter_op="=", value="USA"),
    ]
    vis = Vis(intent, sql_df)
    vis._vis_data = sql_df
    filter_output = SQLExecutor.execute_filter(vis)
    assert (
        filter_output[0]
        == 'WHERE "Origin" = \'USA\' AND "Year" IS NOT NULL AND "Horsepower" IS NOT NULL'
    )
    assert filter_output[1] == ["Origin"]


def test_inequalityfilter():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxSQLTable()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("car")

    vis = Vis(
        [
            lux.Clause(attribute="Horsepower", filter_op=">", value=50),
            lux.Clause(attribute="MilesPerGal"),
        ]
    )
    vis._vis_data = sql_df
    filter_output = SQLExecutor.execute_filter(vis)
    assert filter_output[0] == 'WHERE "Horsepower" > \'50\' AND "MilesPerGal" IS NOT NULL'
    assert filter_output[1] == ["Horsepower"]

    intent = [
        lux.Clause(attribute="Horsepower", filter_op="<=", value=100),
        lux.Clause(attribute="MilesPerGal"),
    ]
    vis = Vis(intent, sql_df)
    vis._vis_data = sql_df
    filter_output = SQLExecutor.execute_filter(vis)
    assert filter_output[0] == 'WHERE "Horsepower" <= \'100\' AND "MilesPerGal" IS NOT NULL'
    assert filter_output[1] == ["Horsepower"]


def test_binning():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxSQLTable()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("car")

    vis = Vis([lux.Clause(attribute="Horsepower")], sql_df)
    nbins = list(filter(lambda x: x.bin_size != 0, vis._inferred_intent))[0].bin_size
    assert len(vis.data) == nbins


def test_record():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxSQLTable()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("car")

    vis = Vis([lux.Clause(attribute="Cylinders")], sql_df)
    assert len(vis.data) == len(sql_df.unique_values["Cylinders"])


def test_filter_aggregation_fillzero_aligned():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxSQLTable()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("car")

    intent = [
        lux.Clause(attribute="Cylinders"),
        lux.Clause(attribute="MilesPerGal"),
        lux.Clause("Origin=Japan"),
    ]
    vis = Vis(intent, sql_df)
    result = vis.data
    assert result[result["Cylinders"] == 5]["MilesPerGal"].values[0] == 0
    assert result[result["Cylinders"] == 8]["MilesPerGal"].values[0] == 0


def test_exclude_attribute():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxSQLTable()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("car")

    intent = [lux.Clause("?", exclude=["Name", "Year"]), lux.Clause("Horsepower")]
    vislist = VisList(intent, sql_df)
    for vis in vislist:
        assert vis.get_attr_by_channel("x")[0].attribute != "Year"
        assert vis.get_attr_by_channel("x")[0].attribute != "name"
        assert vis.get_attr_by_channel("y")[0].attribute != "Year"
        assert vis.get_attr_by_channel("y")[0].attribute != "Year"


def test_null_values():
    # checks that the SQLExecutor has filtered out any None or Null values from its metadata
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    sql_df = lux.LuxSQLTable()
    lux.config.set_SQL_connection(connection)
    sql_df.set_SQL_table("aug_test_table")

    assert None not in sql_df.unique_values["enrolled_university"]
