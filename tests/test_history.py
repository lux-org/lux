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

def _check_log(df, op_name, parent_status=None, cols=None):
    assert df.history[-1].op_name == op_name, "The %s() call is not logged to the child dataframe." % op_name
    assert len(df.history) == 1, "Other function calls are logged to the child dataframe unnecessarily."
    if parent_status is not None:
        assert df.history[-1].kwargs.get("rank_type", None) == parent_status, "The rank type is supposed to be set as %s" % parent_status 
    if cols is not None:
        assert set(df.history[-1].cols) == set(cols), "These columns should be logged as attributes of the event {}".format(cols)

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

def test_fillna(global_var):
    def prepare_NA_df():
        df = pytest.car_df.copy(deep=True)
        with df.history.pause(): # the original dataset does no have any na value.
            df.loc[0, "Miles_per_Gallon"] = None
            df.loc[1, "Horsepower"] = None
        return df
    # test the inplace = False case
    df = prepare_NA_df()
    new_df = df.fillna(0)
    # parent dataframe
    _check_log(df, "fillna", parent_status="parent", cols=['Miles_per_Gallon', 'Horsepower'])
    # child dataframe
    _check_log(new_df, "fillna", parent_status="child", cols=['Miles_per_Gallon', 'Horsepower'])

    # test the inplace = True case
    df = prepare_NA_df()
    new_df = df.fillna(0, inplace=True)
    # parent dataframe
    _check_log(df, "fillna", parent_status="parent", cols=['Miles_per_Gallon', 'Horsepower'])

def test_slice(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = df[1:3]
    # child dataframe
    _check_log(new_df, "slice", parent_status="child")
    # parent dataframe
    _check_log(df, "slice", parent_status="parent")

def test_loc(global_var):
    # case 1: no child dataframe
    df = pytest.car_df.copy(deep=True)
    new_df = df.loc[0,"Weight"]
    _check_log(df, "loc", parent_status="parent", cols=["Weight"])
    
    # case 2: access columns in list
    df = pytest.car_df.copy(deep=True)
    new_df = df.loc[0,["Weight", "Origin"]]
    _check_log(df, "loc", parent_status="parent", cols=["Weight", "Origin"], )
    _check_log(new_df, "loc", parent_status="child", cols=["Weight", "Origin"])
    
    # case 3: access columns in slice
    df = pytest.car_df.copy(deep=True)
    new_df = df.loc[0,:]
    _check_log(df, "loc", parent_status="parent", cols=[])
    _check_log(new_df, "loc", parent_status="child", cols=[])
    
    # case 4: access columns in a tuple of length 1
    df = pytest.car_df.copy(deep=True)
    new_df = df.loc[0,]
    _check_log(df, "loc", parent_status="parent", cols=[])
    _check_log(new_df, "loc", parent_status="child", cols=[])
    
    # case 5: when the child and the parent dataframe are actually the same
    df = pytest.car_df.copy(deep=True)
    new_df = df.loc[:,:]
    _check_log(df, "loc", parent_status="parent", cols=[])
    _check_log(new_df, "loc", parent_status="parent", cols=[])
    
    # case 6: access only by rows
    df = pytest.car_df.copy(deep=True)
    new_df = df.loc[0:2]
    _check_log(df, "loc", parent_status="parent", cols=[])
    _check_log(new_df, "loc", parent_status="child", cols=[])

def test_iloc(global_var):
    # case 1: no child dataframe
    df = pytest.car_df.copy(deep=True)
    new_df = df.iloc[0, 1]
    _check_log(df, "iloc", parent_status="parent", cols=["MilesPerGal"])
    
    # case 2: access columns in list
    df = pytest.car_df.copy(deep=True)
    new_df = df.iloc[0, [2, 3]]
    _check_log(df, "iloc", parent_status="parent", cols=["Displacement", "Cylinders"])
    _check_log(new_df, "iloc", parent_status="child", cols=["Displacement", "Cylinders"])
    
    # case 3: access columns in slice
    df = pytest.car_df.copy(deep=True)
    new_df = df.iloc[0,:]
    _check_log(df, "iloc", parent_status="parent", cols=[])
    _check_log(new_df, "iloc", parent_status="child", cols=[])
    
    # case 4: access columns in a tuple of length 1
    df = pytest.car_df.copy(deep=True)
    new_df = df.iloc[0,]
    _check_log(df, "iloc", parent_status="parent", cols=[])
    _check_log(new_df, "iloc", parent_status="child", cols=[])
    
    # case 5: when the child and the parent dataframe are actually the same
    df = pytest.car_df.copy(deep=True)
    new_df = df.iloc[:,:]
    _check_log(df, "iloc", parent_status="parent", cols=[])
    _check_log(new_df, "iloc", parent_status="parent", cols=[])
    
    # case 6: access only by rows
    df = pytest.car_df.copy(deep=True)
    new_df = df.iloc[0:2]
    _check_log(df, "iloc", parent_status="parent", cols=[])
    _check_log(new_df, "iloc", parent_status="child", cols=[])

def test_aggregate(global_var):
    # case 1: when a list was passed
    df = pytest.car_df.copy(deep=True)
    new_df = df.aggregate(["min"])
    _check_log(df, "min", parent_status="parent", cols=[])
    _check_log(new_df, "min", parent_status="child", cols=[])

    # case 2: when a dict was passed
    df = pytest.car_df.copy(deep=True)
    new_df = df.aggregate({"Year": ["max"]})
    _check_log(df, "max", parent_status="parent", cols=["Year"])
    _check_log(new_df, "max", parent_status="child", cols=["Year"])

def test_sum(global_var):
    df = pytest.car_df.copy(deep=True)
    with df.history.pause():
        df = df[["Name", "Cylinders", "Horsepower", "Origin"]]
    new_df = df.sum()
    _check_log(df, "sum", parent_status="parent", cols=[])
    _check_log(new_df, "sum", parent_status="child", cols=[])

def test_prod(global_var):
    df = pytest.car_df.copy(deep=True)
    with df.history.pause():
        df = df[["Name", "Cylinders", "Horsepower", "Origin"]]
    new_df = df.prod(axis=0)
    _check_log(df, "prod", parent_status="parent", cols=["Cylinders", "Horsepower"])
    _check_log(new_df, "prod", parent_status="child", cols=["Cylinders", "Horsepower"])

def test_max(global_var):
    # df.max()
    df = pytest.car_df.copy(deep=True)
    new_df = df.max()
    _check_log(df, "max", parent_status="parent", cols=[])
    _check_log(new_df, "max", parent_status="child", cols=[])

def test_min(global_var):
    df = pytest.car_df.copy(deep=True)
    with df.history.pause():
        df = df[["Name", "Cylinders", "Horsepower", "Origin"]]
    new_df = df.min()
    _check_log(df, "min", parent_status="parent", cols=[])
    _check_log(new_df, "min", parent_status="child", cols=[])

def test_mean(global_var):
    df = pytest.car_df.copy(deep=True)
    with df.history.pause():
        df = df[["Name", "Cylinders", "Horsepower", "Origin"]]
    new_df = df.mean()
    _check_log(df, "mean", parent_status="parent", cols=["Cylinders", "Horsepower"])
    _check_log(new_df, "mean", parent_status="child", cols=["Cylinders", "Horsepower"])

def test_median(global_var):
    df = pytest.car_df.copy(deep=True)
    with df.history.pause():
        df = df[["Name", "Cylinders", "Horsepower", "Origin"]]
    new_df = df.median()
    _check_log(df, "median", parent_status="parent", cols=["Cylinders", "Horsepower"])
    _check_log(new_df, "median", parent_status="child", cols=["Cylinders", "Horsepower"])

def test_skew(global_var):
    df = pytest.car_df.copy(deep=True)
    with df.history.pause():
        df = df[["Name", "Cylinders", "Horsepower", "Origin"]]
    new_df = df.skew()
    _check_log(df, "skew", parent_status="parent", cols=["Cylinders", "Horsepower"])
    _check_log(new_df, "skew", parent_status="child", cols=["Cylinders", "Horsepower"])

def test_kurt(global_var):
    df = pytest.car_df.copy(deep=True)
    with df.history.pause():
        df = df[["Name", "Cylinders", "Horsepower", "Origin"]]
    new_df = df.kurt()
    _check_log(df, "kurt", parent_status="parent", cols=["Cylinders", "Horsepower"])
    _check_log(new_df, "kurt", parent_status="child", cols=["Cylinders", "Horsepower"])

def test_std(global_var):
    df = pytest.car_df.copy(deep=True)
    with df.history.pause():
        df = df[["Name", "Cylinders", "Horsepower", "Origin"]]
    new_df = df.std()
    _check_log(df, "std", parent_status="parent", cols=["Cylinders", "Horsepower"])
    _check_log(new_df, "std", parent_status="child", cols=["Cylinders", "Horsepower"])

def test_sem(global_var):
    df = pytest.car_df.copy(deep=True)
    with df.history.pause():
        df = df[["Name", "Cylinders", "Horsepower", "Origin"]]
    new_df = df.sem()
    _check_log(df, "sem", parent_status="parent", cols=["Cylinders", "Horsepower"])
    _check_log(new_df, "sem", parent_status="child", cols=["Cylinders", "Horsepower"])

