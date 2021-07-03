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

def _check_log(df, op_name, parent_status=None):
    assert df.history[-1].op_name == op_name, "The %s() call is not logged to the child dataframe." % op_name
    assert len(df.history) == 1, "Other function calls are logged to the child dataframe unnecessarily."
    if parent_status is not None:
        assert df.history[-1].kwargs.get("rank_type", None) == parent_status

def test_head(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = df.head()
    # child dataframe
    _check_log(new_df, "head")
    # parent dataframe
    _check_log(df, "head")

def test_tail(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = df.tail()
    # child dataframe
    _check_log(new_df, "tail")
    # parent dataframe
    _check_log(df, "tail")

def test_info(global_var):
    df = pytest.car_df.copy(deep=True)
    df.info()
    _check_log(df, "info")

def test_describe(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = df.describe()
    # child dataframe
    _check_log(new_df, "describe", parent_status="child")
    # parent dataframe
    _check_log(df, "describe", parent_status="parent")

def test_query(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = df.query("Origin == \"Europe\"")
    # child dataframe
    _check_log(new_df, "query", parent_status="child")
    # parent dataframe
    _check_log(df, "query", parent_status="parent")

def test_isna(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = df.isna()
    # child dataframe
    _check_log(new_df, "isna", parent_status="child")
    # parent dataframe
    _check_log(df, "isna", parent_status="parent")

def test_isnull(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = df.isnull()
    # child dataframe
    _check_log(new_df, "isna", parent_status="child")
    # parent dataframe
    _check_log(df, "isna", parent_status="parent")

def test_notnull(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = df.notnull()
    # child dataframe
    _check_log(new_df, "notnull", parent_status="child")
    # parent dataframe
    _check_log(df, "notnull", parent_status="parent")

def test_notna(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = df.notna()
    # child dataframe
    _check_log(new_df, "notnull", parent_status="child")
    # parent dataframe
    _check_log(df, "notnull", parent_status="parent")

def test_dropna(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = df.dropna()
    # child dataframe
    _check_log(new_df, "dropna", parent_status="child")
    # parent dataframe
    _check_log(df, "dropna", parent_status="parent")
