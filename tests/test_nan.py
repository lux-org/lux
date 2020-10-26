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


def test_nan_column():
    df = pd.read_csv("lux/data/college.csv")
    df["Geography"] = np.nan
    df._repr_html_()
    for visList in df.recommendation.keys():
        for vis in df.recommendation[visList]:
            assert vis.get_attr_by_attr_name("Geography") == []
