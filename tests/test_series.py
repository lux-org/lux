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
import warnings


def test_df_to_series():
    # Ensure metadata is kept when going from df to series
    df = pd.read_csv("lux/data/car.csv")
    df._repr_html_()  # compute metadata
    assert df.cardinality is not None
    series = df["Weight"]
    assert isinstance(series, lux.core.series.LuxSeries), "Derived series is type LuxSeries."
    print(df["Weight"]._metadata)
    assert df["Weight"]._metadata == [
        "_intent",
        "data_type",
        "unique_values",
        "cardinality",
        "_rec_info",
        "_pandas_only",
        "_min_max",
        "plotting_style",
        "_current_vis",
        "_widget",
        "_recommendation",
        "_prev",
        "_history",
        "_saved_export",
        "name",
    ], "Metadata is lost when going from Dataframe to Series."
    assert df.cardinality is not None, "Metadata is lost when going from Dataframe to Series."
    assert series.name == "Weight", "Pandas Series original `name` property not retained."


def test_print_dtypes(global_var):
    df = pytest.college_df
    with warnings.catch_warnings(record=True) as w:
        print(df.dtypes)
        assert len(w) == 0, "Warning displayed when printing dtypes"


def test_print_iterrow(global_var):
    df = pytest.college_df
    with warnings.catch_warnings(record=True) as w:
        for index, row in df.iterrows():
            print(row)
            break
        assert len(w) == 0, "Warning displayed when printing iterrow"
