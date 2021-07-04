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

def _check_log(df, op_name, parent_status=None, cols=None, expected_length=1):
    assert df.history[-1].op_name == op_name, "The %s() call is not logged to the child dataframe." % op_name
    assert len(df.history) == expected_length, "Other function calls are logged to the child dataframe unnecessarily."
    if parent_status is not None:
        assert df.history[-1].kwargs.get("rank_type", None) == parent_status, "The rank type is supposed to be set as %s" % parent_status 
    if cols is not None:
        assert set(df.history[-1].cols) == set(cols), "These columns should be logged as attributes of the event {}".format(cols)

def test_agg(global_var):
    # case 1 when passes a single function
    df = pytest.car_df.copy(deep=True)
    df_groupby = df[["Horsepower", "Brand"]].groupby("Brand")
    _check_log(df_groupby, "groupby")
    new_df = df_groupby.agg(sum)
    _check_log(new_df, "sum", parent_status="child", expected_length=2)
    assert new_df.pre_aggregated

    # case 2 when passes a single function string
    df = pytest.car_df.copy(deep=True)
    df_groupby = df[["Horsepower", "Brand"]].groupby("Brand")
    _check_log(df_groupby, "groupby")
    new_df = df_groupby.agg("mean")
    _check_log(new_df, "mean", parent_status="child", expected_length=2)
    assert new_df.pre_aggregated

    # case 3 when passes a list of functions
    df = pytest.car_df.copy(deep=True)
    df_groupby = df[["Horsepower", "Brand"]].groupby("Brand")
    _check_log(df_groupby, "groupby")
    new_df = df_groupby.agg(["std"])
    _check_log(new_df, "std", parent_status="child", expected_length=2)
    assert new_df.pre_aggregated

    # case 4 when passes a dict
    df = pytest.car_df.copy(deep=True)
    df_groupby = df[["Horsepower", "Brand"]].groupby("Brand")
    _check_log(df_groupby, "groupby")
    new_df = df_groupby.agg({"Horsepower": "var"})
    _check_log(new_df, "var", parent_status="child", cols=["Horsepower"], expected_length=2)
    assert new_df.pre_aggregated



def test_agg_size(global_var):
    df = pytest.car_df.copy(deep=True)
    df_groupby = df[["Horsepower", "Brand", "Year"]].groupby("Brand")
    _check_log(df_groupby, "groupby")
    new_df = df_groupby.size()
    _check_log(new_df, "size", parent_status="child", cols=[], expected_length=2)
    assert new_df.pre_aggregated

def test_agg_mean(global_var):
    df = pytest.car_df.copy(deep=True)
    df_groupby = df[["Horsepower", "Brand", "Year"]].groupby("Brand")
    _check_log(df_groupby, "groupby")
    new_df = df_groupby.mean()
    _check_log(new_df, "mean", parent_status="child", cols=["Horsepower"], expected_length=2)
    assert new_df.pre_aggregated

def test_agg_min(global_var):
    df = pytest.car_df.copy(deep=True)
    df_groupby = df[["Horsepower", "Brand", "Year"]].groupby("Brand")
    _check_log(df_groupby, "groupby")
    new_df = df_groupby.min()
    _check_log(new_df, "min", parent_status="child", cols=["Horsepower", "Year"], expected_length=2)
    assert new_df.pre_aggregated

def test_agg_max(global_var):
    df = pytest.car_df.copy(deep=True)
    df_groupby = df[["Horsepower", "Brand", "Year"]].groupby("Brand")
    _check_log(df_groupby, "groupby")
    new_df = df_groupby.max()
    _check_log(new_df, "max", parent_status="child", cols=["Horsepower", "Year"], expected_length=2)
    assert new_df.pre_aggregated

def test_agg_count(global_var):
    df = pytest.car_df.copy(deep=True)
    df_groupby = df[["Horsepower", "Brand", "Year"]].groupby("Brand")
    _check_log(df_groupby, "groupby")
    new_df = df_groupby.count()
    _check_log(new_df, "count", parent_status="child", cols=[], expected_length=2)
    assert new_df.pre_aggregated

def test_agg_sum(global_var):
    df = pytest.car_df.copy(deep=True)
    df_groupby = df[["Horsepower", "Brand", "Year"]].groupby("Brand")
    _check_log(df_groupby, "groupby")
    new_df = df_groupby.sum()
    _check_log(new_df, "sum", parent_status="child", cols=["Horsepower"], expected_length=2)
    assert new_df.pre_aggregated

def test_agg_prod(global_var):
    df = pytest.car_df.copy(deep=True)
    df_groupby = df[["Horsepower", "Brand", "Year"]].groupby("Brand")
    _check_log(df_groupby, "groupby")
    new_df = df_groupby.prod()
    _check_log(new_df, "prod", parent_status="child", cols=["Horsepower"], expected_length=2)
    assert new_df.pre_aggregated

def test_agg_median(global_var):
    df = pytest.car_df.copy(deep=True)
    df_groupby = df[["Horsepower", "Brand", "Year"]].groupby("Brand")
    _check_log(df_groupby, "groupby")
    new_df = df_groupby.median()
    _check_log(new_df, "median", parent_status="child", cols=["Horsepower"], expected_length=2)
    assert new_df.pre_aggregated

def test_agg_std(global_var):
    df = pytest.car_df.copy(deep=True)
    df_groupby = df[["Horsepower", "Brand", "Year"]].groupby("Brand")
    _check_log(df_groupby, "groupby")
    new_df = df_groupby.std()
    _check_log(new_df, "std", parent_status="child", cols=["Horsepower"], expected_length=2)
    assert new_df.pre_aggregated

def test_agg_var(global_var):
    df = pytest.car_df.copy(deep=True)
    df_groupby = df[["Horsepower", "Brand", "Year"]].groupby("Brand")
    _check_log(df_groupby, "groupby")
    new_df = df_groupby.var()
    _check_log(new_df, "var", parent_status="child", cols=["Horsepower"], expected_length=2)
    assert new_df.pre_aggregated

def test_agg_sem(global_var):
    df = pytest.car_df.copy(deep=True)
    df_groupby = df[["Horsepower", "Brand", "Year"]].groupby("Brand")
    _check_log(df_groupby, "groupby")
    new_df = df_groupby.sem()
    _check_log(new_df, "sem", parent_status="child", cols=["Horsepower"], expected_length=2)
    assert new_df.pre_aggregated


def test_filter(global_var):
    df = pytest.car_df.copy(deep=True)
    df._ipython_display_()
    new_df = df.groupby("Origin").filter(lambda x: x["Weight"].mean() > 3000)
    new_df._ipython_display_()
    assert new_df.history[0].op_name == "groupby"
    assert not new_df.pre_aggregated


def test_get_group(global_var):
    df = pytest.car_df.copy(deep=True)
    df._ipython_display_()
    new_df = df.groupby("Origin").get_group("Japan")
    new_df._ipython_display_()
    assert new_df.history[0].op_name == "groupby"
    assert not new_df.pre_aggregated


def test_series_groupby(global_var):
    df = pytest.car_df.copy(deep=True)
    df._repr_html_()
    new_ser = df.set_index("Brand")["Displacement"].groupby(level=0).agg("mean")
    assert new_ser.history[1].op_name == "groupby"
    assert new_ser.pre_aggregated
