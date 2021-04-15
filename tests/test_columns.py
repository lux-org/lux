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

from lux.vis.Vis import Vis


def test_special_char():
    dataset = [
        {"special.char": 1, "normal": 2},
        {"special.char": 1, "normal": 2},
        {"special.char": 1, "normal": 5},
        {"special.char": 1, "normal": 2},
        {"special.char": 1, "normal": 3},
        {"special.char": 1, "normal": 2},
        {"special.char": 1, "normal": 6},
        {"special.char": 1, "normal": 2},
        {"special.char": 1, "normal": 7},
        {"special.char": 1, "normal": 2},
        {"special.char": 3, "normal": 10},
        {"special.char": 1, "normal": 1},
        {"special.char": 5, "normal": 2},
        {"special.char": 1, "normal": 2},
        {"special.char": 1, "normal": 2},
        {"special.char": 1, "normal": 2},
        {"special.char": 1, "normal": 2},
    ]
    test = pd.DataFrame(dataset)

    from lux.vis.Vis import Vis

    # TODO: add assert that checks that the bar chart is rendered correctly in Altair
    vis = Vis(["special.char"], test)
    assert vis.mark == "bar"
    assert vis.intent == ["special.char"]
    assert vis.get_attr_by_channel("x")[0].attribute == "Record"
    assert vis.get_attr_by_channel("y")[0].attribute == "special.char"
    vis = vis.to_altair()
    assert (
        "alt.Y('specialchar', type= 'nominal', axis=alt.Axis(labelOverlap=True, title='special.char'))"
        in vis
    )
    assert (
        "alt.X('Record', type= 'quantitative', title='Number of Records', axis=alt.Axis(title='Number of Records')"
        in vis
    )
    # Checking that this works even when there are multiple "." in column
    test = test.rename(columns={"special.char": "special..char.."})
    # TODO: add assert that checks that the bar chart is rendered correctly in Altair
    vis = Vis(["special..char.."], test)
    assert vis.mark == "bar"
    assert vis.intent == ["special..char.."]
    assert vis.get_attr_by_channel("x")[0].attribute == "Record"
    assert vis.get_attr_by_channel("y")[0].attribute == "special..char.."
    vis = vis.to_altair()
    assert (
        "alt.Y('specialchar', type= 'nominal', axis=alt.Axis(labelOverlap=True, title='special..char..')"
        in vis
    )
    assert (
        "alt.X('Record', type= 'quantitative', title='Number of Records', axis=alt.Axis(title='Number of Records')"
        in vis
    )


long_var = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."


def test_abbrev_bar():
    dataset = [
        {long_var: 1, "normal": 3},
        {long_var: 1, "normal": 3},
        {long_var: 1, "normal": 2},
        {long_var: 1, "normal": 4},
    ]
    test = pd.DataFrame(dataset)
    vis = Vis([long_var, "normal"], test).to_altair()
    assert "axis=alt.Axis(labelOverlap=True, title='Lorem ipsum dol...t laborum.')" in vis


def test_abbrev_histogram():
    dataset = [
        {long_var: 1},
        {long_var: 0},
    ]
    test = pd.DataFrame(dataset)
    vis = Vis([long_var], test).to_altair()
    assert "axis=alt.Axis(labelOverlap=True, title='Lorem ipsu...aborum. (binned)')" in vis


def test_abbrev_scatter():
    dataset = [
        {long_var: 1, "normal": 3},
    ]
    test = pd.DataFrame(dataset)
    vis = Vis([long_var, "normal"], test).to_altair()
    assert "axis=alt.Axis(title='Lorem ipsum dol...t laborum.')" in vis


def test_abbrev_agg():
    dataset = [
        {"normal": "USA", long_var: 3},
        {"normal": "Europe", long_var: 3},
        {"normal": "USA", long_var: 2},
        {"normal": "Europe", long_var: 4},
    ]
    test = pd.DataFrame(dataset)
    vis = Vis([long_var, "normal"], test).to_altair()
    assert "axis=alt.Axis(title='Mean of Lorem ipsum dol...')" in vis


def test_int_columns(global_var):
    df = pd.read_csv("lux/data/college.csv")
    df.columns = range(len(df.columns))
    assert list(df.recommendation.keys()) == ["Correlation", "Distribution", "Occurrence"]
    df.intent = [8, 3]
    assert list(df.recommendation.keys()) == ["Enhance", "Filter", "Generalize"]
    df.intent = [0]
    assert list(df.recommendation.keys()) == ["Enhance", "Filter"]


def test_name_column(global_var):
    df = pd.read_csv("lux/data/car.csv")
    new_df = df.rename(columns={"Name": "name"})
    assert list(new_df.recommendation.keys()) == [
        "Correlation",
        "Distribution",
        "Occurrence",
        "Temporal",
    ]
    assert len(new_df.recommendation["Correlation"])
    assert new_df["name"][0] != None
    assert (new_df["name"].unique() != None)[0]
