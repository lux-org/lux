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


def test_head_tail(global_var):
    df = pytest.car_df
    df._ipython_display_()
    assert df._message.to_html() == ""
    df.head()._ipython_display_()
    assert (
        "Lux is visualizing the previous version of the dataframe before you applied <code>head</code>."
        in df._message.to_html()
    )
    df._ipython_display_()
    assert df._message.to_html() == ""
    df.tail()._ipython_display_()
    assert (
        "Lux is visualizing the previous version of the dataframe before you applied <code>tail</code>."
        in df._message.to_html()
    )


def test_describe(global_var):
    df = pytest.college_df
    summary = df.describe()
    summary._ipython_display_()
    assert len(summary.columns) == 10


def test_groupby_describe(global_var):
    df = pytest.college_df
    result = df.groupby("FundingModel")["AdmissionRate"].describe()
    result._ipython_display_()
    assert result.shape == (3, 8)


def test_convert_dtype(global_var):
    df = pytest.college_df
    cdf = df.convert_dtypes()
    cdf._ipython_display_()
    assert list(cdf.recommendation.keys()) == ["Correlation", "Distribution", "Occurrence"]
