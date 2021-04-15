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
from lux.utils import date_utils
from lux.executor.PandasExecutor import PandasExecutor


def test_dateformatter(global_var):
    ldf = pd.read_csv("lux/data/car.csv")
    # change pandas dtype for the column "Year" to datetype
    ldf["Year"] = pd.to_datetime(ldf["Year"], format="%Y")
    timestamp = np.datetime64("2019-08-26")
    ldf.maintain_metadata()
    assert date_utils.date_formatter(timestamp, ldf) == "2019"

    ldf["Year"][0] = np.datetime64("1970-03-01")  # make month non unique

    assert date_utils.date_formatter(timestamp, ldf) == "2019-8"

    ldf["Year"][0] = np.datetime64("1970-03-03")  # make day non unique

    assert date_utils.date_formatter(timestamp, ldf) == "2019-8-26"


def test_period_selection(global_var):
    ldf = pd.read_csv("lux/data/car.csv")
    ldf["Year"] = pd.to_datetime(ldf["Year"], format="%Y")

    ldf["Year"] = pd.DatetimeIndex(ldf["Year"]).to_period(freq="A")

    ldf.set_intent(
        [
            lux.Clause(attribute=["Horsepower", "Weight", "Acceleration"]),
            lux.Clause(attribute="Year"),
        ]
    )

    lux.config.executor.execute(ldf.current_vis, ldf)

    assert all([type(vlist.data) == lux.core.frame.LuxDataFrame for vlist in ldf.current_vis])
    assert all(ldf.current_vis[2].data.columns == ["Year", "Acceleration"])


def test_period_filter(global_var):
    ldf = pd.read_csv("lux/data/car.csv")
    ldf["Year"] = pd.to_datetime(ldf["Year"], format="%Y")
    ldf["Year"] = pd.DatetimeIndex(ldf["Year"]).to_period(freq="A")

    from lux.vis.Vis import Vis

    vis = Vis(["Acceleration", "Horsepower", "Year=1972"], ldf)
    assert ldf.data_type["Year"] == "temporal"
    assert isinstance(vis._inferred_intent[2].value, str)


def test_period_to_altair(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df["Year"] = pd.DatetimeIndex(df["Year"]).to_period(freq="A")
    from lux.vis.Vis import Vis

    vis = Vis(["Acceleration", "Horsepower", "Year=1972"], df)
    exported_code = vis.to_altair()

    assert "Year = 1972" in exported_code


def test_refresh_inplace():
    df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-02-01", "2020-03-01", "2020-04-01"],
            "value": [10.5, 15.2, 20.3, 25.2],
        }
    )
    with pytest.warns(UserWarning, match="Lux detects that the attribute 'date' may be temporal."):
        df._ipython_display_()
    assert df.data_type["date"] == "temporal"

    from lux.vis.Vis import Vis

    vis = Vis(["date", "value"], df)

    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df.maintain_metadata()
    inverted_data_type = lux.config.executor.invert_data_type(df.data_type)
    assert inverted_data_type["temporal"][0] == "date"

    vis.refresh_source(df)
    assert vis.mark == "line"
    assert vis.get_attr_by_channel("x")[0].attribute == "date"
    assert vis.get_attr_by_channel("y")[0].attribute == "value"
