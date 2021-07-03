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

def test_head(global_var):
    df = pytest.car_df.copy(deep=True)
    df._ipython_display_()
    new_df = df.head()
    new_df._ipython_display_()
    assert new_df.history[0].op_name == "head"
    assert df.history[-1].op_name == "head"

def test_tail(global_var):
    df = pytest.car_df.copy(deep=True)
    df._ipython_display_()
    new_df = df.tail()
    new_df._ipython_display_()
    assert new_df.history[0].op_name == "tail"
    assert df.history[-1].op_name == "tail"

def test_info(global_var):
    df = pytest.car_df.copy(deep=True)
    df._ipython_display_()
    df.info()
    assert df.history[-1].op_name == "info"

