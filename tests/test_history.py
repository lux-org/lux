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

def test_head(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = df.head()
    # child dataframe
    assert new_df.history[-1].op_name == "head", "The head() call is not logged to the child dataframe."
    assert len(new_df.history) == 1, "Other function calls are logged to the child dataframe unnecessarily."
    # parent dataframe
    assert df.history[-1].op_name == "head", "The head() call is not logged to the parent dataframe."
    assert len(df.history) == 1, "Other function calls are logged to the parent dataframe unnecessarily."

def test_tail(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = df.tail()
    # child dataframe
    assert new_df.history[-1].op_name == "tail", "The tail() call is not logged to the child dataframe."
    assert len(new_df.history) == 1, "Other function calls are logged to the child dataframe unnecessarily."
    # parent dataframe
    assert df.history[-1].op_name == "tail", "The tail() call is not logged to the parent dataframe."
    assert len(df.history) == 1, "Other function calls are logged to the parent dataframe unnecessarily."

def test_info(global_var):
    df = pytest.car_df.copy(deep=True)
    df.info()
    assert df.history[-1].op_name == "info", "The info() call is not logged to the dataframe."
    assert len(df.history) == 1, "Other function calls are logged to the parent dataframe unnecessarily."

def test_describe(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = df.describe()
    # child dataframe
    assert new_df.history[-1].op_name == "describe", "The describe() call is not logged to the child dataframe."
    assert len(new_df.history) == 1, "Other function calls are logged to the child dataframe unnecessarily."
    assert new_df.history[-1].kwargs.get("rank_type", None) == "child"
    # parent dataframe
    assert df.history[-1].op_name == "describe", "The describe() call is not logged to the parent dataframe."
    assert len(df.history) == 1, "Other function calls are logged to the parent dataframe unnecessarily."
    assert df.history[-1].kwargs.get("rank_type", None) == "parent"

def test_query(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = df.query("Origin == \"Europe\"")
    # child dataframe
    assert new_df.history[-1].op_name == "query", "The query() call is not logged to the child dataframe."
    assert len(new_df.history) == 1, "Other function calls are logged to the child dataframe unnecessarily."
    assert new_df.history[-1].kwargs.get("rank_type", None) == "child"
    # parent dataframe
    assert df.history[-1].op_name == "query", "The query() call is not logged to the parent dataframe."
    assert len(df.history) == 1, "Other function calls are logged to the parent dataframe unnecessarily."
    assert df.history[-1].kwargs.get("rank_type", None) == "parent"

def test_isna(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = pd.isna(df)
    # child dataframe
    assert new_df.history[-1].op_name == "isna", "The isna() call is not logged to the child dataframe."
    assert len(new_df.history) == 1, "Other function calls are logged to the child dataframe unnecessarily."
    assert new_df.history[-1].kwargs.get("rank_type", None) == "child"
    # parent dataframe
    assert df.history[-1].op_name == "isna", "The isna() call is not logged to the parent dataframe."
    assert len(df.history) == 1, "Other function calls are logged to the parent dataframe unnecessarily."
    assert df.history[-1].kwargs.get("rank_type", None) == "parent"

def test_isnull(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = pd.isnull(df)
    # child dataframe
    assert new_df.history[-1].op_name == "isna", "The isna() call is not logged to the child dataframe."
    assert len(new_df.history) == 1, "Other function calls are logged to the child dataframe unnecessarily."
    assert new_df.history[-1].kwargs.get("rank_type", None) == "child"
    # parent dataframe
    assert df.history[-1].op_name == "isna", "The isna() call is not logged to the parent dataframe."
    assert len(df.history) == 1, "Other function calls are logged to the parent dataframe unnecessarily."
    assert df.history[-1].kwargs.get("rank_type", None) == "parent"