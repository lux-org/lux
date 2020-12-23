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
    vis = vis.to_Altair()
    assert "axis=alt.Axis(labelOverlap=True, title='specialchar')" in vis
    # Checking that this works even when there are multiple "." in column
    test = test.rename(columns={"special.char": "special..char.."})
    # TODO: add assert that checks that the bar chart is rendered correctly in Altair
    vis = Vis(["special..char.."], test)
    assert vis.mark == "bar"
    assert vis.intent == ["special..char.."]
    assert vis.get_attr_by_channel("x")[0].attribute == "Record"
    assert vis.get_attr_by_channel("y")[0].attribute == "special..char.."
    vis = vis.to_Altair()
    assert "axis=alt.Axis(labelOverlap=True, title='specialchar')" in vis


def test_abbrev_bar():
    long_var = "The teacher provides supports, encouragement, and opportunities equally well for all students in the class, across all sub-groups"
    dataset = [
        {long_var: 1},
    ]
    test = pd.DataFrame(dataset)
    vis = test.recommendation["Column Groups"][0].to_Altair()
    assert "axis=alt.Axis(title='The teacher pro...sub-groups'" in vis


def test_abbrev_histogram():
    long_var = "The teacher provides supports, encouragement, and opportunities equally well for all students in the class, across all sub-groups"
    dataset = [
        {long_var: 1},
        {long_var: 0},
    ]
    test = pd.DataFrame(dataset)
    vis = Vis([long_var], test).to_Altair()
    "axis=alt.Axis(labelOverlap=True, title='The teache...-groups (binned)')" in vis


def test_abbrev_scatter():
    long_var = "The teacher provides supports, encouragement, and opportunities equally well for all students in the class, across all sub-groups"
    dataset = [
        {long_var: 1, "normal": 3},
    ]
    test = pd.DataFrame(dataset)
    vis = Vis([long_var, "normal"], test).to_Altair()
    "axis=alt.Axis(title='The teacher pro...sub-groups'))" in vis
