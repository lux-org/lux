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
from lux.vis.VisList import VisList
from lux.vis.Vis import Vis


def test_vis():
    url = (
        "https://github.com/lux-org/lux-datasets/blob/master/data/olympic.csv?raw=true"
    )
    df = pd.read_csv(url)
    vis = Vis(["Height", "SportType=Ball"], df)
    assert vis.get_attr_by_attr_name("Height")[0].bin_size != 0
    assert vis.get_attr_by_attr_name("Record")[0].aggregation == "count"


def test_vis_set_specs():
    url = (
        "https://github.com/lux-org/lux-datasets/blob/master/data/olympic.csv?raw=true"
    )
    df = pd.read_csv(url)
    vis = Vis(["Height", "SportType=Ball"], df)
    vis.set_intent(["Height", "SportType=Ice"])
    assert vis.get_attr_by_attr_name("SportType")[0].value == "Ice"


def test_vis_collection():
    url = (
        "https://github.com/lux-org/lux-datasets/blob/master/data/olympic.csv?raw=true"
    )
    df = pd.read_csv(url)
    vlist = VisList(["Height", "SportType=Ball", "?"], df)
    vis_with_year = list(
        filter(lambda x: x.get_attr_by_attr_name("Year") != [], vlist)
    )[0]
    assert vis_with_year.get_attr_by_channel("x")[0].attribute == "Year"
    assert (
        len(vlist) == len(df.columns) - 1 - 1
    )  # remove 1 for vis with same filter attribute and remove 1 vis with for same attribute
    vlist = VisList(["Height", "?"], df)
    assert len(vlist) == len(df.columns) - 1  # remove 1 for vis with for same attribute


def test_vis_collection_set_intent():
    url = (
        "https://github.com/lux-org/lux-datasets/blob/master/data/olympic.csv?raw=true"
    )
    df = pd.read_csv(url)
    vlist = VisList(["Height", "SportType=Ice", "?"], df)
    vlist.set_intent(["Height", "SportType=Boat", "?"])
    for v in vlist._collection:
        filter_vspec = list(filter(lambda x: x.channel == "", v._inferred_intent))[0]
        assert filter_vspec.value == "Boat"


def test_custom_plot_setting():
    def change_color_make_transparent_add_title(chart):
        chart = chart.configure_mark(color="green", opacity=0.2)
        chart.title = "Test Title"
        return chart

    df = pd.read_csv("lux/data/car.csv")
    df.plot_config = change_color_make_transparent_add_title
    df._repr_html_()
    config_mark_addition = 'chart = chart.configure_mark(color="green", opacity=0.2)'
    title_addition = 'chart.title = "Test Title"'
    exported_code_str = df.recommendation["Correlation"][0].to_Altair()
    assert config_mark_addition in exported_code_str
    assert title_addition in exported_code_str


def test_remove():
    df = pd.read_csv("lux/data/car.csv")
    vis = Vis([lux.Clause("Horsepower"), lux.Clause("Acceleration")], df)
    vis.remove_column_from_spec("Horsepower", remove_first=False)
    assert vis._inferred_intent[0].attribute == "Acceleration"


def test_remove_identity():
    df = pd.read_csv("lux/data/car.csv")
    vis = Vis(["Horsepower", "Horsepower"], df)
    vis.remove_column_from_spec("Horsepower")
    assert vis._inferred_intent == [], "Remove all instances of Horsepower"

    df = pd.read_csv("lux/data/car.csv")
    vis = Vis(["Horsepower", "Horsepower"], df)
    vis.remove_column_from_spec("Horsepower", remove_first=True)
    assert len(vis._inferred_intent) == 1, "Remove only 1 instances of Horsepower"
    assert (
        vis._inferred_intent[0].attribute == "Horsepower"
    ), "Remove only 1 instances of Horsepower"


def test_refresh_collection():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df.set_intent(
        [lux.Clause(attribute="Acceleration"), lux.Clause(attribute="Horsepower")]
    )
    df._repr_html_()
    enhanceCollection = df.recommendation["Enhance"]
    enhanceCollection.refresh_source(df[df["Origin"] == "USA"])


def test_vis_custom_aggregation_as_str():
    df = pd.read_csv("lux/data/college.csv")
    import numpy as np

    vis = Vis(["HighestDegree", lux.Clause("AverageCost", aggregation="max")], df)
    assert vis.get_attr_by_data_model("measure")[0].aggregation == "max"
    assert vis.get_attr_by_data_model("measure")[0]._aggregation_name == "max"


def test_vis_custom_aggregation_as_numpy_func():
    df = pd.read_csv("lux/data/college.csv")
    from lux.vis.Vis import Vis
    import numpy as np

    vis = Vis(["HighestDegree", lux.Clause("AverageCost", aggregation=np.ptp)], df)
    assert vis.get_attr_by_data_model("measure")[0].aggregation == np.ptp
    assert vis.get_attr_by_data_model("measure")[0]._aggregation_name == "ptp"


def test_vis_collection_via_list_of_vis():
    url = (
        "https://github.com/lux-org/lux-datasets/blob/master/data/olympic.csv?raw=true"
    )
    df = pd.read_csv(url)
    df["Year"] = pd.to_datetime(
        df["Year"], format="%Y"
    )  # change pandas dtype for the column "Year" to datetype
    from lux.vis.VisList import VisList
    from lux.vis.Vis import Vis

    vcLst = []
    for attribute in ["Sport", "Year", "Height", "HostRegion", "SportType"]:
        vis = Vis([lux.Clause("Weight"), lux.Clause(attribute)])
        vcLst.append(vis)
    vlist = VisList(vcLst, df)
    assert len(vlist) == 5


def test_vis_to_Altair_basic_df():
    df = pd.read_csv("lux/data/car.csv")
    vis = Vis(["Weight", "Horsepower"], df)
    code = vis.to_Altair()
    assert "alt.Chart(df)" in code, "Unable to export to Altair"


def test_vis_to_Altair_custom_named_df():
    df = pd.read_csv("lux/data/car.csv")
    some_weirdly_named_df = df.dropna()
    vis = Vis(["Weight", "Horsepower"], some_weirdly_named_df)
    code = vis.to_Altair()
    assert (
        "alt.Chart(some_weirdly_named_df)" in code
    ), "Unable to export to Altair and detect custom df name"


def test_vis_to_Altair_standalone():
    df = pd.read_csv("lux/data/car.csv")
    vis = Vis(["Weight", "Horsepower"], df)
    code = vis.to_Altair(standalone=True)
    assert (
        "chart = alt.Chart(pd.DataFrame({'Weight': {0: 3504, 1: 3693, 2: 3436, 3: 3433, 4: 3449, 5: 43"
        in code
        or "alt.Chart(pd.DataFrame({'Horsepower': {0: 130, 1: 165, 2: 150, 3: 150, 4: 140,"
        in code
    )


def test_vis_list_custom_title_override():
    url = (
        "https://github.com/lux-org/lux-datasets/blob/master/data/olympic.csv?raw=true"
    )
    df = pd.read_csv(url)
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")

    vcLst = []
    for attribute in ["Sport", "Year", "Height", "HostRegion", "SportType"]:
        vis = Vis(
            [lux.Clause("Weight"), lux.Clause(attribute)],
            title="overriding dummy title",
        )
        vcLst.append(vis)
    vlist = VisList(vcLst, df)
    for v in vlist:
        assert v.title == "overriding dummy title"


def test_vis_set_intent():
    from lux.vis.Vis import Vis

    df = pd.read_csv("lux/data/car.csv")
    vis = Vis(["Weight", "Horsepower"], df)
    vis._repr_html_()
    assert "Horsepower" in str(vis._code)
    vis.intent = ["Weight", "MilesPerGal"]
    vis._repr_html_()
    assert "MilesPerGal" in str(vis._code)


def test_vis_list_set_intent():
    from lux.vis.VisList import VisList

    df = pd.read_csv("lux/data/car.csv")
    vislist = VisList(["Horsepower", "?"], df)
    vislist._repr_html_()
    for vis in vislist:
        assert vis.get_attr_by_attr_name("Horsepower") != []
    vislist.intent = ["Weight", "?"]
    vislist._repr_html_()
    for vis in vislist:
        assert vis.get_attr_by_attr_name("Weight") != []


def test_text_not_overridden():
    from lux.vis.Vis import Vis

    df = pd.read_csv("lux/data/college.csv")
    vis = Vis(["Region", "Geography"], df)
    vis._repr_html_()
    code = vis.to_Altair()
    assert 'color = "#ff8e04"' in code
