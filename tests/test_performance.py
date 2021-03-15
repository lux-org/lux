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
import time


# To run the script and see the printed result, run:
# python -m pytest -s tests/test_performance.py
def test_q1_performance_census(global_var):
    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/census.csv?raw=true")
    tic = time.perf_counter()
    df._ipython_display_()
    toc = time.perf_counter()
    delta = toc - tic
    df._ipython_display_()
    toc2 = time.perf_counter()
    delta2 = toc2 - toc
    print(f"1st display Performance: {delta:0.4f} seconds")
    print(f"2nd display Performance: {delta2:0.4f} seconds")
    assert (
        delta < 4.5
    ), "The recommendations on Census dataset took a total of {delta:0.4f} seconds, longer than expected."
    assert (
        delta2 < 0.15 < delta
    ), "Subsequent display of recommendations on Census dataset took a total of {delta2:0.4f} seconds, longer than expected."

    assert df.data_type == {
        "age": "quantitative",
        "workclass": "nominal",
        "fnlwgt": "quantitative",
        "education": "nominal",
        "education-num": "nominal",
        "marital-status": "nominal",
        "occupation": "nominal",
        "relationship": "nominal",
        "race": "nominal",
        "sex": "nominal",
        "capital-gain": "quantitative",
        "capital-loss": "quantitative",
        "hours-per-week": "quantitative",
        "native-country": "nominal",
        "income": "nominal",
    }
