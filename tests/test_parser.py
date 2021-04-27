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

import pandas as pd
import lux
import pytest


def test_case1(global_var):
    df = pytest.car_df
    df.set_intent(["Horsepower"])
    assert type(df._intent[0]) is lux.Clause
    assert df._intent[0].attribute == "Horsepower"
    df.clear_intent()


def test_case2(global_var):
    df = pytest.car_df
    df.set_intent(["Horsepower", lux.Clause("MilesPerGal", channel="x")])
    assert type(df._intent[0]) is lux.Clause
    assert df._intent[0].attribute == "Horsepower"
    assert type(df._intent[1]) is lux.Clause
    assert df._intent[1].attribute == "MilesPerGal"
    df.clear_intent()


def test_case3(global_var):
    df = pytest.car_df
    df.set_intent(["Horsepower", "Origin=USA"])
    assert type(df._intent[0]) is lux.Clause
    assert df._intent[0].attribute == "Horsepower"
    assert type(df._intent[1]) is lux.Clause
    assert df._intent[1].attribute == "Origin"
    assert df._intent[1].value == "USA"
    df.clear_intent()


def test_case4(global_var):
    df = pytest.car_df
    df.set_intent(["Horsepower", "Origin=USA|Japan"])
    assert type(df._intent[0]) is lux.Clause
    assert df._intent[0].attribute == "Horsepower"
    assert type(df._intent[1]) is lux.Clause
    assert df._intent[1].attribute == "Origin"
    assert df._intent[1].value == ["USA", "Japan"]
    df.clear_intent()


def test_case5(global_var):
    df = pytest.car_df
    df.set_intent([["Horsepower", "MilesPerGal", "Weight"], "Origin=USA"])
    assert type(df._intent[0]) is lux.Clause
    assert df._intent[0].attribute == ["Horsepower", "MilesPerGal", "Weight"]
    assert type(df._intent[1]) is lux.Clause
    assert df._intent[1].attribute == "Origin"
    assert df._intent[1].value == "USA"

    df.set_intent(["Horsepower|MilesPerGal|Weight", "Origin=USA"])
    assert type(df._intent[0]) is lux.Clause
    assert df._intent[0].attribute == ["Horsepower", "MilesPerGal", "Weight"]
    assert type(df._intent[1]) is lux.Clause
    assert df._intent[1].attribute == "Origin"
    assert df._intent[1].value == "USA"
    df.clear_intent()


def test_case6(global_var):
    df = pytest.car_df
    df.set_intent(["Horsepower", "Origin=?"])
    df._ipython_display_()
    assert type(df._intent[0]) is lux.Clause
    assert df._intent[0].attribute == "Horsepower"
    assert type(df._intent[1]) is lux.Clause
    assert df._intent[1].attribute == "Origin"
    assert df._intent[1].value == ["USA", "Japan", "Europe"]
    df.clear_intent()


def test_case7(global_var):
    df = pytest.car_df
    df.intent = [["Horsepower", "MilesPerGal", "Acceleration"], "Origin"]
    df._ipython_display_()
    assert len(df.current_vis) == 3
    df.clear_intent()


def test_validator_invalid_value(global_var):
    df = pytest.college_df
    with pytest.warns(
        UserWarning,
        match="The input value 'bob' does not exist for the attribute 'Region' for the DataFrame.",
    ):
        df.intent = ["Region=bob"]

    df.clear_intent()


def test_validator_invalid_filter(global_var):
    df = pytest.college_df

    with pytest.warns(
        UserWarning,
        match="The input 'New England' looks like a value that belongs to the 'Region' attribute.",
    ):
        df.intent = ["New England", "Southeast", "Far West"]


def test_validator_invalid_attribute(global_var):
    df = pytest.college_df
    with pytest.warns(
        UserWarning,
        match="The input attribute 'blah' does not exist in the DataFrame.",
    ):
        df.intent = ["blah"]
