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
from lux.vis.Vis import Vis
from lux.executor.SQLExecutor import SQLExecutor


def test_scatter_code_export(global_var):
    tbl = lux.LuxSQLTable()
    tbl.set_SQL_table("cars")

    vis = Vis([lux.Clause("horsepower"), lux.Clause("acceleration")], tbl)
    SQLExecutor.execute([vis], tbl)
    code = vis.to_code("python")
    try:
        exec(code, globals())
        create_chart_data(tbl, vis)
    except:
        assert False


def test_color_scatter_code_export(global_var):
    tbl = lux.LuxSQLTable()
    tbl.set_SQL_table("cars")

    vis = Vis([lux.Clause("horsepower"), lux.Clause("acceleration"), lux.Clause("origin")], tbl)
    SQLExecutor.execute([vis], tbl)
    code = vis.to_code("python")
    try:
        exec(code, globals())
        create_chart_data(tbl, vis)
    except:
        assert False


def test_histogram_code_export(global_var):
    tbl = lux.LuxSQLTable()
    tbl.set_SQL_table("cars")

    vis = Vis([lux.Clause("horsepower")], tbl)
    SQLExecutor.execute([vis], tbl)
    code = vis.to_code("python")
    try:
        exec(code, globals())
        create_chart_data(tbl, vis)
    except:
        assert False


def test_barchart_code_export(global_var):
    tbl = lux.LuxSQLTable()
    tbl.set_SQL_table("cars")

    vis = Vis([lux.Clause("origin")], tbl)
    SQLExecutor.execute([vis], tbl)
    code = vis.to_code("python")
    try:
        exec(code, globals())
        create_chart_data(tbl, vis)
    except:
        assert False


def test_color_barchart_code_export(global_var):
    tbl = lux.LuxSQLTable()
    tbl.set_SQL_table("cars")

    vis = Vis([lux.Clause("origin"), lux.Clause("cylinders")], tbl)
    SQLExecutor.execute([vis], tbl)
    code = vis.to_code("python")
    try:
        exec(code, globals())
        create_chart_data(tbl, vis)
    except:
        assert False


# def test_heatmap_code_export(global_var):
#     tbl = lux.LuxSQLTable()
#     tbl.set_SQL_table("airbnb")
#     lux.config._heatmap_start = 100

#     vis = Vis(["price", "longitude"], tbl)
#     SQLExecutor.execute([vis], tbl)
#     code = vis.to_code("python")
#     try:
#         exec(code, globals())
#         create_chart_data(tbl, vis)
#     except:
#         assert False

#     lux.config._heatmap_start = 5000
