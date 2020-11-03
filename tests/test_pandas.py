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

# def test_df_to_series():
#     # Ensure metadata is kept when going from df to series
#     df = pd.read_csv("lux/data/car.csv")
#     df._repr_html_() # compute metadata
#     assert df.cardinality is not None
#     series = df["Weight"]
#     assert isinstance(series,lux.core.series.LuxSeries), "Derived series is type LuxSeries."
#     assert df["Weight"]._metadata == ['name','_intent', 'data_type_lookup', 'data_type', 'data_model_lookup', 'data_model', 'unique_values', 'cardinality', 'min_max', 'plot_config', '_current_vis', '_widget', '_recommendation'], "Metadata is lost when going from Dataframe to Series."
#     assert df.cardinality is not None, "Metadata is lost when going from Dataframe to Series."
#     assert series.name == "Weight", "Pandas Series original `name` property not retained."


def test_head_tail():
    df = pd.read_csv("lux/data/car.csv")
    df._repr_html_()
    assert df._message.to_html() == ""
    df.head()._repr_html_()
    assert (
        "Lux is visualizing the previous version of the dataframe before you applied <code>head</code>."
        in df._message.to_html()
    )
    df._repr_html_()
    assert df._message.to_html() == ""
    df.tail()._repr_html_()
    assert (
        "Lux is visualizing the previous version of the dataframe before you applied <code>tail</code>."
        in df._message.to_html()
    )
