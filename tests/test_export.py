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
from lux.executor.PandasExecutor import PandasExecutor


def test_scatter_code_export(global_var):
    df = pytest.car_df

    vis = Vis([lux.Clause("Horsepower"), lux.Clause("Acceleration")], df)
    PandasExecutor.execute([vis], df)
    code = vis.to_code("python")
    try:
        exec(code, globals())
        create_chart_data(df, vis)
    except:
        assert False


def test_color_scatter_code_export(global_var):
    df = pytest.car_df

    vis = Vis([lux.Clause("Horsepower"), lux.Clause("Acceleration"), lux.Clause("Origin")], df)
    PandasExecutor.execute([vis], df)
    code = vis.to_code("python")
    try:
        exec(code, globals())
        create_chart_data(df, vis)
    except:
        assert False


def test_histogram_code_export(global_var):
    df = pytest.car_df

    vis = Vis([lux.Clause("Horsepower")], df)
    PandasExecutor.execute([vis], df)
    code = vis.to_code("python")
    try:
        exec(code, globals())
        create_chart_data(df, vis)
    except:
        assert False


def test_barchart_code_export(global_var):
    df = pytest.car_df

    vis = Vis([lux.Clause("Origin")], df)
    PandasExecutor.execute([vis], df)
    code = vis.to_code("python")
    try:
        exec(code, globals())
        create_chart_data(df, vis)
    except:
        assert False


def test_color_barchart_code_export(global_var):
    df = pytest.car_df

    vis = Vis([lux.Clause("Origin"), lux.Clause("Cylinders")], df)
    PandasExecutor.execute([vis], df)
    code = vis.to_code("python")
    try:
        exec(code, globals())
        create_chart_data(df, vis)
    except:
        assert False


def test_heatmap_code_export(global_var):
    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/airbnb_nyc.csv")
    lux.config._heatmap_start = 100

    vis = Vis(["price", "longitude"], df)
    PandasExecutor.execute([vis], df)
    code = vis.to_code("python")

    try:
        exec(code, globals())
        create_chart_data(df, vis)
    except:
        assert False

    lux.config._heatmap_start = 5000
