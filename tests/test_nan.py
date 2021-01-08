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
    df._repr_html_()
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
    vis._repr_html_()
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
    ldf._repr_html_()
    assert ldf.recommendation["Occurrence"][0].mark == "bar"
