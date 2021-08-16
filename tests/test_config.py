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
        vlist.sort()
        vlist = vlist.showK()
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
        lux.config.register_action("bars", random_categorical, contain_horsepower)
    else:
        lux.config.register_action("bars", random_categorical)
    return df


def test_default_actions_registered(global_var):
    lux.config.set_executor_type("Pandas")
    df = pytest.car_df
    df._ipython_display_()
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
    df._ipython_display_()
    assert (
        "bars" not in df.recommendation,
        "Bars should not be rendered when there is no intent 'horsepower' specified.",
    )


def test_pass_validator():
    df = register_new_action()
    df.set_intent(["Acceleration", "Horsepower"])
    df._ipython_display_()
    assert len(df.recommendation["bars"]) > 0
    assert (
        "bars" in df.recommendation,
        "Bars should be rendered when intent 'horsepower' is specified.",
    )


def test_no_validator():
    df = register_new_action(False)
    df._ipython_display_()
    assert len(df.recommendation["bars"]) > 0
    assert "bars" in df.recommendation


def test_invalid_function(global_var):
    df = pd.read_csv("lux/data/car.csv")
    with pytest.raises(ValueError, match="Action must be a callable"):
        lux.config.register_action("bars", "not a Callable")


def test_invalid_validator(global_var):
    df = pd.read_csv("lux/data/car.csv")

    def random_categorical(ldf):
        intent = [lux.Clause("?", data_type="nominal")]
        vlist = VisList(intent, ldf)
        for vis in vlist:
            vis.score = 10
        vlist.sort()
        vlist = vlist.showK()
        return {
            "action": "bars",
            "description": "Random list of Bar charts",
            "collection": vlist,
        }

    with pytest.raises(ValueError, match="Display condition must be a callable"):
        lux.config.register_action("bars", random_categorical, "not a Callable")


def test_remove_action():
    df = register_new_action()
    df.set_intent(["Acceleration", "Horsepower"])
    df._ipython_display_()
    assert (
        "bars" in df.recommendation,
        "Bars should be rendered after it has been registered with correct intent.",
    )
    assert (
        len(df.recommendation["bars"]) > 0,
        "Bars should be rendered after it has been registered with correct intent.",
    )
    lux.config.remove_action("bars")
    df._ipython_display_()
    assert (
        "bars" not in df.recommendation,
        "Bars should not be rendered after it has been removed.",
    )
    df.clear_intent()


def test_remove_invalid_action(global_var):
    df = pd.read_csv("lux/data/car.csv")
    with pytest.raises(ValueError, match="Option 'bars' has not been registered"):
        lux.config.remove_action("bars")


# TODO: This test does not pass in pytest but is working in Jupyter notebook.
def test_remove_default_actions(global_var):
    df = pytest.car_df
    df._ipython_display_()

    lux.config.remove_action("distribution")
    df._ipython_display_()
    assert "Distribution" not in df.recommendation

    lux.config.remove_action("occurrence")
    df._ipython_display_()
    assert "Occurrence" not in df.recommendation

    lux.config.remove_action("temporal")
    df._ipython_display_()
    assert "Temporal" not in df.recommendation

    lux.config.remove_action("correlation")
    df._ipython_display_()
    assert "Correlation" not in df.recommendation

    assert (
        len(df.recommendation) == 0,
        "Default actions should not be rendered after it has been removed.",
    )

    df = register_new_action()
    df.set_intent(["Acceleration", "Horsepower"])
    df._ipython_display_()
    assert (
        "bars" in df.recommendation,
        "Bars should be rendered after it has been registered with correct intent.",
    )
    assert len(df.recommendation["bars"]) > 0
    df.clear_intent()

    from lux.action.default import register_default_actions

    register_default_actions()


def test_matplotlib_set_default_plotting_style():
    lux.config.plotting_backend = "matplotlib"

    def add_title(fig, ax):
        ax.set_title("Test Title")
        return fig, ax

    df = pd.read_csv("lux/data/car.csv")
    lux.config.plotting_style = add_title
    df._ipython_display_()
    title_addition = 'ax.set_title("Test Title")'
    exported_code_str = df.recommendation["Correlation"][0].to_altair()
    assert title_addition in exported_code_str


def test_set_default_plotting_style():
    lux.config.plotting_backend = "vegalite"

    def change_color_make_transparent_add_title(chart):
        chart = chart.configure_mark(color="green", opacity=0.2)
        chart.title = "Test Title"
        return chart

    df = pd.read_csv("lux/data/car.csv")
    lux.config.plotting_style = change_color_make_transparent_add_title
    df._ipython_display_()
    config_mark_addition = 'chart = chart.configure_mark(color="green", opacity=0.2)'
    title_addition = 'chart.title = "Test Title"'
    exported_code_str = df.recommendation["Correlation"][0].to_altair()
    assert config_mark_addition in exported_code_str
    assert title_addition in exported_code_str


def test_sampling_flag_config():
    lux.config.heatmap = False
    lux.config.sampling = True
    lux.config.early_pruning = False
    import numpy as np

    N = int(1.1 * lux.config.sampling_cap)
    df = pd.DataFrame({"col1": np.random.rand(N), "col2": np.random.rand(N)})
    df.maintain_recs()
    assert len(df.recommendation["Correlation"][0].data) == lux.config.sampling_cap
    lux.config.sampling = True
    lux.config.heatmap = True
    lux.config.early_pruning = True


def test_sampling_parameters_config():
    df = pd.read_csv("lux/data/car.csv")
    df._ipython_display_()
    assert df.recommendation["Correlation"][0].data.shape[0] == 392
    lux.config.sampling_start = 50
    lux.config.sampling_cap = 100
    df = pd.read_csv("lux/data/car.csv")
    df._ipython_display_()
    assert df.recommendation["Correlation"][0].data.shape[0] == 100
    lux.config.sampling_cap = 30000
    lux.config.sampling_start = 10000


def test_heatmap_flag_config():
    lux.config.heatmap = True
    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/airbnb_nyc.csv")
    df._ipython_display_()
    assert df.recommendation["Correlation"][0]._postbin
    lux.config.heatmap = False
    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/airbnb_nyc.csv")
    df._ipython_display_()
    assert not df.recommendation["Correlation"][0]._postbin
    lux.config.heatmap = True


def test_topk(global_var):
    df = pd.read_csv("lux/data/college.csv")
    lux.config.topk = False
    df._ipython_display_()
    assert len(df.recommendation["Correlation"]) == 45, "Turn off top K"
    lux.config.topk = 20
    df = pd.read_csv("lux/data/college.csv")
    df._ipython_display_()
    assert len(df.recommendation["Correlation"]) == 20, "Show top 20"
    for vis in df.recommendation["Correlation"]:
        assert vis.score > 0.2


def test_sort(global_var):
    df = pd.read_csv("lux/data/college.csv")
    lux.config.topk = 15
    df._ipython_display_()
    assert len(df.recommendation["Correlation"]) == 15, "Show top 15"
    for vis in df.recommendation["Correlation"]:
        assert vis.score > 0.5
    df = pd.read_csv("lux/data/college.csv")
    lux.config.sort = "ascending"
    df._ipython_display_()
    assert len(df.recommendation["Correlation"]) == 15, "Show bottom 15"
    for vis in df.recommendation["Correlation"]:
        assert vis.score < 0.35

    lux.config.sort = "none"
    df = pd.read_csv("lux/data/college.csv")
    df._ipython_display_()
    scorelst = [x.score for x in df.recommendation["Distribution"]]
    assert sorted(scorelst) != scorelst, "unsorted setting"
    lux.config.sort = "descending"


# TODO: This test does not pass in pytest but is working in Jupyter notebook.
# def test_plot_setting(global_var):
# 	df = pytest.car_df
# 	df["Year"] = pd.to_datetime(df["Year"], format='%Y')
# 	def change_color_add_title(chart):
# 		chart = chart.configure_mark(color="green") # change mark color to green
# 		chart.title = "Custom Title" # add title to chart
# 		return chart

# 	df.plot_config = change_color_add_title

# 	df._ipython_display_()

# 	vis_code = df.recommendation["Correlation"][0].to_altair()
# 	print (vis_code)
# 	assert 'chart = chart.configure_mark(color="green")' in vis_code, "Exported chart does not have additional plot style setting."
