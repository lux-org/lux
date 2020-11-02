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
from lux.vis.VisList import VisList
import lux


def register_new_action(validator: bool = True):
    df = pd.read_csv("lux/data/car.csv")

    def random_categorical(ldf):
        intent = [lux.Clause("?", data_type="nominal")]
        vlist = VisList(intent, ldf)
        for vis in vlist:
            vis.score = 10
        vlist = vlist.topK(15)
        return {
            "action": "bars",
            "description": "Random list of Bar charts",
            "collection": vlist,
        }

    def contain_horsepower(df):
        for clause in df.intent:
            if clause.get_attr() == "Horsepower":
                return True
        return False

    if validator:
        lux.register_action("bars", random_categorical, contain_horsepower)
    else:
        lux.register_action("bars", random_categorical)
    return df


def test_default_actions_registered():
    df = pd.read_csv("lux/data/car.csv")
    df._repr_html_()
    assert "Distribution" in df.recommendation
    assert len(df.recommendation["Distribution"]) > 0

    assert "Occurrence" in df.recommendation
    assert len(df.recommendation["Occurrence"]) > 0

    assert "Temporal" in df.recommendation
    assert len(df.recommendation["Temporal"]) > 0

    assert "Correlation" in df.recommendation
    assert len(df.recommendation["Correlation"]) > 0


def test_fail_validator():
    df = register_new_action()
    df._repr_html_()
    assert (
        "bars" not in df.recommendation,
        "Bars should not be rendered when there is no intent 'horsepower' specified.",
    )


def test_pass_validator():
    df = register_new_action()
    df.set_intent(["Acceleration", "Horsepower"])
    df._repr_html_()
    assert len(df.recommendation["bars"]) > 0
    assert (
        "bars" in df.recommendation,
        "Bars should be rendered when intent 'horsepower' is specified.",
    )


def test_no_validator():
    df = register_new_action(False)
    df._repr_html_()
    assert len(df.recommendation["bars"]) > 0
    assert "bars" in df.recommendation


def test_invalid_function():
    df = pd.read_csv("lux/data/car.csv")
    with pytest.raises(ValueError, match="Value must be a callable"):
        lux.register_action("bars", "not a Callable")


def test_invalid_validator():
    df = pd.read_csv("lux/data/car.csv")

    def random_categorical(ldf):
        intent = [lux.Clause("?", data_type="nominal")]
        vlist = VisList(intent, ldf)
        for vis in vlist:
            vis.score = 10
        vlist = vlist.topK(15)
        return {
            "action": "bars",
            "description": "Random list of Bar charts",
            "collection": vlist,
        }

    with pytest.raises(ValueError, match="Value must be a callable"):
        lux.register_action("bars", random_categorical, "not a Callable")


def test_remove_action():
    df = register_new_action()
    df.set_intent(["Acceleration", "Horsepower"])
    df._repr_html_()
    assert (
        "bars" in df.recommendation,
        "Bars should be rendered after it has been registered with correct intent.",
    )
    assert (
        len(df.recommendation["bars"]) > 0,
        "Bars should be rendered after it has been registered with correct intent.",
    )
    lux.remove_action("bars")
    df._repr_html_()
    assert (
        "bars" not in df.recommendation,
        "Bars should not be rendered after it has been removed.",
    )


def test_remove_invalid_action():
    df = pd.read_csv("lux/data/car.csv")
    with pytest.raises(ValueError, match="Option 'bars' has not been registered"):
        lux.remove_action("bars")


def test_remove_default_actions():
    df = pd.read_csv("lux/data/car.csv")
    df._repr_html_()

    lux.remove_action("Distribution")
    df._repr_html_()
    assert "Distribution" not in df.recommendation

    lux.remove_action("Occurrence")
    df._repr_html_()
    assert "Occurrence" not in df.recommendation

    lux.remove_action("Temporal")
    df._repr_html_()
    assert "Temporal" not in df.recommendation

    lux.remove_action("Correlation")
    df._repr_html_()
    assert "Correlation" not in df.recommendation

    assert (
        len(df.recommendation) == 0,
        "Default actions should not be rendered after it has been removed.",
    )

    df = register_new_action()
    df.set_intent(["Acceleration", "Horsepower"])
    df._repr_html_()
    assert (
        "bars" in df.recommendation,
        "Bars should be rendered after it has been registered with correct intent.",
    )
    assert len(df.recommendation["bars"]) > 0


# TODO: This test does not pass in pytest but is working in Jupyter notebook.
# def test_plot_setting():
# 	df = pd.read_csv("lux/data/car.csv")
# 	df["Year"] = pd.to_datetime(df["Year"], format='%Y')
# 	def change_color_add_title(chart):
# 		chart = chart.configure_mark(color="green") # change mark color to green
# 		chart.title = "Custom Title" # add title to chart
# 		return chart

# 	df.plot_config = change_color_add_title

# 	df._repr_html_()

# 	vis_code = df.recommendation["Correlation"][0].to_Altair()
# 	print (vis_code)
# 	assert 'chart = chart.configure_mark(color="green")' in vis_code, "Exported chart does not have additional plot style setting."
