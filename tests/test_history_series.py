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

def test_unique(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = df["Cylinders"]
    unique_values = new_df.unique()
    _check_log(df, "unique", parent_status="parent", cols=["Cylinders"])
    _check_log(df, "unique", cols=["Cylinders"])

def test_value_counts(global_var):
    df = pytest.car_df.copy(deep=True)
    new_df = df["Cylinders"]
    ret_df = new_df.value_counts()
    _check_log(df, "value_counts", parent_status="parent", cols=["Cylinders"])
    _check_log(ret_df, "value_counts", parent_status="child", cols=["Cylinders"])
    _check_log(new_df, "value_counts", cols=["Cylinders"])