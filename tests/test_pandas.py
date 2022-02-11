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
from tempfile import TemporaryDirectory
from pathlib import Path


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


def test_infs():
    nrows = 100_000

    # continuous
    c1 = np.random.uniform(0, 1, size=nrows)
    c1[2] = np.inf
    c2 = np.random.uniform(0, 1, size=nrows)
    c2[3] = np.inf

    # discrete
    d1 = np.random.randint(0, 2, size=nrows)
    d2 = np.random.randint(0, 2, size=nrows)

    df = pd.DataFrame({"c1": c1, "c2": c2, "d1": d1, "d2": d2})

    df._ipython_display_()


def test_timedeltas():
    nrows = 100_000

    c1 = np.random.uniform(0, 10, size=nrows)
    c2 = c1.astype("timedelta64[ms]")

    df = pd.DataFrame({"c1": c1, "c2": c2})

    df._ipython_display_()


def test_datetime_index():
    nrows = 10

    # create a datetime index, freq in seconds
    dt = pd.date_range("1/1/2019", periods=nrows, freq="1s")

    # continuous
    c1 = np.random.uniform(0, 1, size=nrows)

    data = np.random.uniform(0, 1, size=(nrows, 50))
    df = pd.DataFrame(data, index=dt)

    df._ipython_display_()


def test_interval():
    nrows = 100_000

    c1 = pd.Interval(left=0, right=nrows)
    c2 = np.random.uniform(0, 10, size=nrows)

    df = pd.DataFrame({"c1": c1, "c2": c2})

    df._ipython_display_()


def test_datetime_index_serialize():
    nrows = 100000

    # create a datetime index, freq in seconds
    dt = pd.date_range("1/1/2019", periods=nrows, freq="1s")

    # continuous
    c1 = np.random.uniform(0, 1, size=nrows)

    df = pd.DataFrame({"c1": c1}, index=dt)

    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        df.to_csv(tmpdir / "test.csv")
        df = pd.read_csv(tmpdir / "test.csv", names=["date", "c1"], index_col="date", header=0)

    df._ipython_display_()


def test_cut_mixed_types():

    a = [1, "2", 3, "4", 5, "6", 7, "8", 9, "10"] * 1000
    b = np.random.uniform(0, 1, size=len(a))

    df = pd.DataFrame({"a": a, "b": b})

    df._ipython_display_()
