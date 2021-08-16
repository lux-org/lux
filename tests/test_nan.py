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

from lux.vis.Vis import Vis


def test_nan_column(global_var):
    df = pytest.college_df
    old_geo = df["Geography"]
    df["Geography"] = np.nan
    df._ipython_display_()
    for visList in df.recommendation.keys():
        for vis in df.recommendation[visList]:
            assert vis.get_attr_by_attr_name("Geography") == []
    df["Geography"] = old_geo


def test_nan_data_type_detection():
    import numpy as np

    dataset = [
        {"fully_nan": np.nan, "some_nan": 3.0, "some_nan2": np.nan},
        {"fully_nan": np.nan, "some_nan": 15.0, "some_nan2": 3.0},
        {"fully_nan": np.nan, "some_nan": np.nan, "some_nan2": 3.0},
        {"fully_nan": np.nan, "some_nan": 7.0, "some_nan2": 0.0},
        {"fully_nan": np.nan, "some_nan": 2.0, "some_nan2": 2.0},
        {"fully_nan": np.nan, "some_nan": 3.0, "some_nan2": np.nan},
        {"fully_nan": np.nan, "some_nan": 1.0, "some_nan2": 1.0},
        {"fully_nan": np.nan, "some_nan": 1.0, "some_nan2": 1.0},
        {"fully_nan": np.nan, "some_nan": 2.0, "some_nan2": 0.0},
        {"fully_nan": np.nan, "some_nan": 11.0, "some_nan2": 0.0},
    ]
    test = pd.DataFrame(dataset)
    test.maintain_metadata()
    inverted_data_type = lux.config.executor.invert_data_type(test.data_type)
    assert inverted_data_type["nominal"] == [
        "fully_nan",
        "some_nan",
        "some_nan2",
    ], "Categorical columns containing NaNs should be treated as nominal data type"
    nona_test = test.dropna(subset=["some_nan"])
    nona_test.maintain_metadata()
    inverted_data_type = lux.config.executor.invert_data_type(nona_test.data_type)
    assert inverted_data_type["nominal"] == [
        "fully_nan",
        "some_nan",
        "some_nan2",
    ], "Categorical float columns without NaNs should still be categorical, even after dropping NaNs"


def test_apply_nan_filter():
    from lux.vis.Vis import Vis

    import numpy as np

    dataset = [
        {"fully_nan": np.nan, "some_nan": 3.0, "some_nan2": np.nan},
        {"fully_nan": np.nan, "some_nan": 15.0, "some_nan2": 3.0},
        {"fully_nan": np.nan, "some_nan": np.nan, "some_nan2": 3.0},
        {"fully_nan": np.nan, "some_nan": 7.0, "some_nan2": 0.0},
        {"fully_nan": np.nan, "some_nan": 2.0, "some_nan2": 2.0},
        {"fully_nan": np.nan, "some_nan": 3.0, "some_nan2": np.nan},
        {"fully_nan": np.nan, "some_nan": 1.0, "some_nan2": 1.0},
        {"fully_nan": np.nan, "some_nan": 1.0, "some_nan2": 1.0},
        {"fully_nan": np.nan, "some_nan": 2.0, "some_nan2": 0.0},
        {"fully_nan": np.nan, "some_nan": 11.0, "some_nan2": 0.0},
    ]
    test = pd.DataFrame(dataset)

    vis = Vis(["some_nan", "some_nan2=nan"], test)
    vis._ipython_display_()
    assert vis.mark == "bar"


def test_nan_series_occurence():
    from lux.core.series import LuxSeries
    from math import nan

    dvalues = {
        1: " dummy ",
        2: " dummy ",
        3: nan,
        4: " dummy ",
        5: nan,
        6: " dummy ",
        7: " dummy ",
        8: nan,
        9: " dummy ",
        10: nan,
        11: " dummy ",
        12: nan,
        13: nan,
        14: " dummy ",
        15: " dummy ",
    }
    nan_series = LuxSeries(dvalues)
    ldf = pd.DataFrame(nan_series, columns=["col"])
    ldf._ipython_display_()
    assert ldf.recommendation["Occurrence"][0].mark == "bar"


def test_numeric_with_nan():
    # df = pd.read_html(
    #     "http://web.archive.org/web/20200309053509/https://archive.ics.uci.edu/ml/datasets.php?format=&task=&att=&area=&numAtt=&numIns=&type=&sort=nameUp&view=table"
    # )[7]
    # df.columns = df.loc[0]
    # df = df.loc[1:]
    # df = df[['# Instances','# Attributes']]
    # df = df.sample(15)
    # df.to_dict(orient="records")
    from numpy import nan

    df = pd.DataFrame(
        [
            {"# Instances": nan, "# Attributes": nan},
            {"# Instances": "989818", "# Attributes": nan},
            {"# Instances": "303", "# Attributes": "75"},
            {"# Instances": nan, "# Attributes": nan},
            {"# Instances": nan, "# Attributes": nan},
            {"# Instances": "745000", "# Attributes": "411"},
            {"# Instances": "65554", "# Attributes": "29"},
            {"# Instances": "640", "# Attributes": nan},
            {"# Instances": "6435", "# Attributes": "36"},
            {"# Instances": "270", "# Attributes": "13"},
            {"# Instances": "182", "# Attributes": "13"},
            {"# Instances": "22632", "# Attributes": "70"},
            {"# Instances": "3960456", "# Attributes": "4"},
            {"# Instances": "2500", "# Attributes": "10000"},
            {"# Instances": "3850505", "# Attributes": "52"},
        ]
    )
    assert (
        df.data_type["# Instances"] == "quantitative"
    ), "Testing a numeric columns with NaN, check if type can be detected correctly"
    assert (
        df.data_type["# Attributes"] == "quantitative"
    ), "Testing a numeric columns with NaN, check if type can be detected correctly"
    a = df[["# Instances", "# Attributes"]]
    a._ipython_display_()
    assert (
        len(a.recommendation["Distribution"]) == 2
    ), "Testing a numeric columns with NaN, check that histograms are displayed"
    assert "contains missing values" in a._message.to_html(), "Warning message for NaN displayed"
    # a = a.dropna()
    # # TODO: Needs to be explicitly called, possible problem with metadata prpogation
    # a._ipython_display_()
    # assert (
    #     len(a.recommendation["Distribution"]) == 2
    # ), "Example where dtype might be off after dropna(), check if histograms are still displayed"
    assert "" in a._message.to_html(), "No warning message for NaN should be displayed"


def test_empty_filter(global_var):
    df = pytest.car_df
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    fdf = df[df["Origin"] == "U"]
    fdf._ipython_display_()
    assert fdf.data_type == None
    assert len(df[df["Origin"] == "U"]) == 0
