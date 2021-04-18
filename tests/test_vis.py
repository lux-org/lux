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


def test_vis(global_var):
    df = pytest.olympic
    vis = Vis(["Height", "SportType=Ball"], df)
    assert vis.get_attr_by_attr_name("Height")[0].bin_size != 0
    assert vis.get_attr_by_attr_name("Record")[0].aggregation == "count"


def test_vis_set_specs(global_var):
    df = pytest.olympic
    vis = Vis(["Height", "SportType=Ball"], df)
    vis.set_intent(["Height", "SportType=Ice"])
    assert vis.get_attr_by_attr_name("SportType")[0].value == "Ice"
    df.clear_intent()


def test_vis_collection(global_var):
    df = pytest.olympic
    vlist = VisList(["Height", "SportType=Ball", "?"], df)
    vis_with_year = list(filter(lambda x: x.get_attr_by_attr_name("Year") != [], vlist))[0]
    assert vis_with_year.get_attr_by_channel("x")[0].attribute == "Year"
    # remove 1 for vis with same filter attribute and remove 1 vis with for same attribute
    assert len(vlist) == len(df.columns) - 1 - 1
    vlist = VisList(["Height", "?"], df)
    assert len(vlist) == len(df.columns) - 1  # remove 1 for vis with for same attribute


def test_vis_collection_set_intent(global_var):
    df = pytest.olympic
    vlist = VisList(["Height", "SportType=Ice", "?"], df)
    vlist.set_intent(["Height", "SportType=Boat", "?"])
    for v in vlist._collection:
        filter_vspec = list(filter(lambda x: x.channel == "", v._inferred_intent))[0]
        assert filter_vspec.value == "Boat"
    df.clear_intent()


def test_remove(global_var):
    df = pytest.car_df
    vis = Vis([lux.Clause("Horsepower"), lux.Clause("Acceleration")], df)
    vis.remove_column_from_spec("Horsepower", remove_first=False)
    assert vis._inferred_intent[0].attribute == "Acceleration"


def test_remove_identity(global_var):
    df = pytest.car_df
    vis = Vis(["Horsepower", "Horsepower"], df)
    vis.remove_column_from_spec("Horsepower")
    assert vis._inferred_intent == [], "Remove all instances of Horsepower"

    df = pytest.car_df
    vis = Vis(["Horsepower", "Horsepower"], df)
    vis.remove_column_from_spec("Horsepower", remove_first=True)
    assert len(vis._inferred_intent) == 1, "Remove only 1 instances of Horsepower"
    assert vis._inferred_intent[0].attribute == "Horsepower", "Remove only 1 instances of Horsepower"


def test_refresh_collection(global_var):
    df = pytest.car_df
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df.set_intent([lux.Clause(attribute="Acceleration"), lux.Clause(attribute="Horsepower")])
    df._ipython_display_()
    enhanceCollection = df.recommendation["Enhance"]
    enhanceCollection.refresh_source(df[df["Origin"] == "USA"])
    df.clear_intent()


def test_vis_custom_aggregation_as_str(global_var):
    df = pytest.college_df
    import numpy as np

    vis = Vis(["HighestDegree", lux.Clause("AverageCost", aggregation="max")], df)
    assert vis.get_attr_by_data_model("measure")[0].aggregation == "max"
    assert vis.get_attr_by_data_model("measure")[0]._aggregation_name == "max"


def test_vis_custom_aggregation_as_numpy_func(global_var):
    df = pytest.college_df
    from lux.vis.Vis import Vis
    import numpy as np

    vis = Vis(["HighestDegree", lux.Clause("AverageCost", aggregation=np.ptp)], df)
    assert vis.get_attr_by_data_model("measure")[0].aggregation == np.ptp
    assert vis.get_attr_by_data_model("measure")[0]._aggregation_name == "ptp"


def test_vis_collection_via_list_of_vis(global_var):
    df = pytest.olympic
    # change pandas dtype for the column "Year" to datetype
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    from lux.vis.VisList import VisList
    from lux.vis.Vis import Vis

    vcLst = []
    for attribute in ["Sport", "Year", "Height", "HostRegion", "SportType"]:
        vis = Vis([lux.Clause("Weight"), lux.Clause(attribute)])
        vcLst.append(vis)
    vlist = VisList(vcLst, df)
    assert len(vlist) == 5


def test_vis_to_altair_basic_df(global_var):
    df = pytest.car_df
    vis = Vis(["Weight", "Horsepower"], df)
    code = vis.to_altair()
    assert "alt.Chart(df)" in code, "Unable to export to Altair"


def test_vis_to_altair_custom_named_df(global_var):
    df = pytest.car_df
    some_weirdly_named_df = df.dropna()
    vis = Vis(["Weight", "Horsepower"], some_weirdly_named_df)
    code = vis.to_altair()
    assert (
        "alt.Chart(some_weirdly_named_df)" in code
    ), "Unable to export to Altair and detect custom df name"


def test_vis_to_altair_standalone(global_var):
    df = pytest.car_df
    vis = Vis(["Weight", "Horsepower"], df)
    code = vis.to_altair(standalone=True)
    assert (
        "chart = alt.Chart(pd.DataFrame({'Weight': {0: 3504, 1: 3693, 2: 3436, 3: 3433, 4: 3449, 5: 43"
        in code
        or "alt.Chart(pd.DataFrame({'Horsepower': {0: 130, 1: 165, 2: 150, 3: 150, 4: 140," in code
    )


def test_vis_list_custom_title_override(global_var):
    df = pytest.olympic
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


def test_vis_set_intent(global_var):
    from lux.vis.Vis import Vis

    df = pytest.car_df
    vis = Vis(["Weight", "Horsepower"], df)
    vis._ipython_display_()
    assert "Horsepower" in str(vis._code)
    vis.intent = ["Weight", "MilesPerGal"]
    vis._ipython_display_()
    assert "MilesPerGal" in str(vis._code)


def test_vis_list_set_intent(global_var):
    from lux.vis.VisList import VisList

    df = pytest.car_df
    vislist = VisList(["Horsepower", "?"], df)
    vislist._ipython_display_()
    for vis in vislist:
        assert vis.get_attr_by_attr_name("Horsepower") != []
    vislist.intent = ["Weight", "?"]
    vislist._ipython_display_()
    for vis in vislist:
        assert vis.get_attr_by_attr_name("Weight") != []


def test_text_not_overridden():
    from lux.vis.Vis import Vis

    df = pd.read_csv("lux/data/college.csv")
    vis = Vis(["Region", "Geography"], df)
    vis._ipython_display_()
    code = vis.to_altair()
    assert 'color = "#ff8e04"' in code


def test_bar_chart(global_var):
    df = pytest.car_df
    lux.config.plotting_backend = "vegalite"
    vis = Vis(["Origin", "Acceleration"], df)
    vis_code = vis.to_altair()
    assert "alt.Chart(visData).mark_bar()" in vis_code
    assert (
        "y = alt.Y('Origin', type= 'nominal', axis=alt.Axis(labelOverlap=True, title='Origin'))"
        in vis_code
    )
    assert (
        "x = alt.X('Acceleration', type= 'quantitative', title='Mean of Acceleration', axis=alt.Axis(title='Mean of Acceleration'))"
        in vis_code
    )

    lux.config.plotting_style = None
    lux.config.plotting_backend = "matplotlib"
    vis = Vis(["Origin", "Acceleration"], df)
    vis_code = vis.to_matplotlib()
    assert "ax.barh(bars, measurements, align='center')" in vis_code
    assert "ax.set_xlabel('Acceleration')" in vis_code
    assert "ax.set_ylabel('Origin')" in vis_code


def test_colored_bar_chart(global_var):
    df = pytest.car_df
    lux.config.plotting_backend = "vegalite"
    vis = Vis(["Cylinders", "Acceleration", "Origin"], df)
    vis_code = vis.to_altair()
    assert "alt.Chart(visData).mark_bar()" in vis_code
    assert (
        "y = alt.Y('Cylinders', type= 'nominal', axis=alt.Axis(labelOverlap=True, title='Cylinders'))"
        in vis_code
    )
    assert (
        "x = alt.X('Acceleration', type= 'quantitative', title='Mean of Acceleration', axis=alt.Axis(title='Mean of Acceleration')"
        in vis_code
    )

    lux.config.plotting_backend = "matplotlib"
    vis = Vis(["Cylinders", "Acceleration", "Origin"], df)
    vis_code = vis.to_matplotlib()
    assert "ax.barh" in vis_code
    assert "title='Origin'" in vis_code
    assert "ax.set_xlabel('Acceleration')" in vis_code
    assert "ax.set_ylabel('Cylinders')" in vis_code


def test_bar_uniform():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df["Type"] = "A"
    vis = Vis(["Type"], df)
    vis_code = vis.to_altair()
    assert "y = alt.Y('Type', type= 'nominal'" in vis_code


def test_scatter_chart(global_var):
    df = pytest.car_df
    lux.config.plotting_backend = "vegalite"
    vis = Vis(["Acceleration", "Weight"], df)
    vis_code = vis.to_altair()
    assert "alt.Chart(df).mark_circle()" in vis_code
    assert (
        "x=alt.X('Acceleration',scale=alt.Scale(domain=(8.0, 24.8)),type='quantitative', axis=alt.Axis(title='Acceleration'))"
        in vis_code
    )
    assert (
        " y=alt.Y('Weight',scale=alt.Scale(domain=(1613, 5140)),type='quantitative', axis=alt.Axis(title='Weight'))"
        in vis_code
    )

    lux.config.plotting_backend = "matplotlib"
    vis = Vis(["Acceleration", "Weight"], df)
    vis_code = vis.to_matplotlib()
    assert "ax.scatter(x_pts, y_pts, alpha=0.5)" in vis_code
    assert (
        "ax.set_xlabel('Acceleration', fontsize='15')" in vis_code
        or "ax.set_xlabel('Acceleration')" in vis_code
    )
    assert "ax.set_ylabel('Weight', fontsize='15')" in vis_code or "ax.set_ylabel('Weight')" in vis_code


def test_colored_scatter_chart(global_var):
    df = pytest.car_df
    lux.config.plotting_backend = "vegalite"
    vis = Vis(["Origin", "Acceleration", "Weight"], df)
    vis_code = vis.to_altair()
    assert "alt.Chart(df).mark_circle()" in vis_code
    assert (
        "x=alt.X('Acceleration',scale=alt.Scale(domain=(8.0, 24.8)),type='quantitative', axis=alt.Axis(title='Acceleration'))"
        in vis_code
    )
    assert (
        " y=alt.Y('Weight',scale=alt.Scale(domain=(1613, 5140)),type='quantitative', axis=alt.Axis(title='Weight'))"
        in vis_code
    )

    lux.config.plotting_backend = "matplotlib"
    vis = Vis(["Origin", "Acceleration", "Weight"], df)
    vis_code = vis.to_matplotlib()
    assert "ax.scatter" in vis_code
    assert "title='Origin'" in vis_code
    assert (
        "ax.set_xlabel('Acceleration', fontsize='15')" in vis_code
        or "ax.set_xlabel('Acceleration')" in vis_code
    )
    assert "ax.set_ylabel('Weight', fontsize='15')" in vis_code or "ax.set_ylabel('Weight')" in vis_code


def test_line_chart(global_var):
    df = pytest.car_df
    lux.config.plotting_backend = "vegalite"
    vis = Vis(["Year", "Acceleration"], df)
    vis_code = vis.to_altair()
    assert "alt.Chart(visData).mark_line()" in vis_code
    assert (
        "y = alt.Y('Acceleration', type= 'quantitative', title='Mean of Acceleration', axis=alt.Axis(title='Acceleration')"
        in vis_code
    )
    assert "x = alt.X('Year', type = 'temporal', axis=alt.Axis(title='Year'))" in vis_code

    lux.config.plotting_backend = "matplotlib"
    vis = Vis(["Year", "Acceleration"], df)
    vis_code = vis.to_matplotlib()
    assert "ax.plot(x_pts, y_pts)" in vis_code
    assert "ax.set_xlabel('Year')" in vis_code
    assert "ax.set_ylabel('Mean of Acceleration')" in vis_code


def test_colored_line_chart(global_var):
    df = pd.read_csv("lux/data/car.csv")
    lux.config.plotting_backend = "vegalite"
    vis = Vis(["Year", "Acceleration", "Origin"], df)
    vis_code = vis.to_altair()
    assert "alt.Chart(visData).mark_line()" in vis_code
    assert (
        "y = alt.Y('Acceleration', type= 'quantitative', title='Mean of Acceleration', axis=alt.Axis(title='Acceleration')"
        in vis_code
    )
    assert "x = alt.X('Year', type = 'temporal', axis=alt.Axis(title='Year'))" in vis_code

    lux.config.plotting_backend = "matplotlib"
    vis = Vis(["Year", "Acceleration", "Origin"], df)
    vis_code = vis.to_matplotlib()
    assert "ax.plot" in vis_code
    assert "title='Origin'" in vis_code
    assert "ax.set_xlabel('Year')" in vis_code
    assert "ax.set_ylabel('Mean of Acceleration')" in vis_code


def test_histogram_chart(global_var):
    df = pytest.car_df
    lux.config.plotting_backend = "vegalite"
    vis = Vis(["Displacement"], df)
    vis_code = vis.to_altair()
    assert "alt.Chart(visData).mark_bar" in vis_code
    assert (
        "alt.X('Displacement', title='Displacement (binned)',bin=alt.Bin(binned=True, step=38.7), type='quantitative', axis=alt.Axis(labelOverlap=True, title='Displacement (binned)'), scale=alt.Scale(domain=(68.0, 455.0)))"
        in vis_code
    )
    assert 'alt.Y("Number of Records", type="quantitative")' in vis_code

    lux.config.plotting_backend = "matplotlib"
    vis = Vis(["Displacement"], df)
    vis_code = vis.to_matplotlib()
    assert "ax.bar(bars, measurements, width=32.25)" in vis_code
    assert "ax.set_xlabel('Displacement (binned)')" in vis_code
    assert "ax.set_ylabel('Number of Records')" in vis_code


def test_histogram_uniform():
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df["Units"] = 4.0
    vis = Vis(["Units"], df)
    vis_code = vis.to_altair()
    assert "y = alt.Y('Units', type= 'nominal'" in vis_code


def test_heatmap_chart(global_var):
    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/airbnb_nyc.csv")
    lux.config.plotting_backend = "vegalite"
    vis = Vis(["price", "longitude"], df)
    vis_code = vis.to_altair()
    assert "alt.Chart(visData).mark_rect()" in vis_code
    assert (
        "x=alt.X('xBinStart', type='quantitative', axis=alt.Axis(title='price'), bin = alt.BinParams(binned=True))"
        in vis_code
    )
    assert "x2=alt.X2('xBinEnd')" in vis_code
    assert (
        "y=alt.Y('yBinStart', type='quantitative', axis=alt.Axis(title='longitude'), bin = alt.BinParams(binned=True))"
        in vis_code
    )
    assert "y2=alt.Y2('yBinEnd')" in vis_code
    assert 'scale=alt.Scale(type="log")' in vis_code

    lux.config.plotting_backend = "matplotlib"
    vis = Vis(["price", "longitude"], df)
    vis_code = vis.to_matplotlib()
    assert "plt.imshow(df, cmap='Blues')" in vis_code
    assert "index='xBinStart'" in vis_code
    assert "values='count'" in vis_code
    assert "columns='yBinStart'" in vis_code


def test_colored_heatmap_chart(global_var):
    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/airbnb_nyc.csv")
    lux.config.plotting_backend = "vegalite"
    vis = Vis(["price", "longitude", "availability_365"], df)
    vis_code = vis.to_altair()
    assert "alt.Chart(visData).mark_rect()" in vis_code
    assert (
        "x=alt.X('xBinStart', type='quantitative', axis=alt.Axis(title='price'), bin = alt.BinParams(binned=True))"
        in vis_code
    )
    assert "x2=alt.X2('xBinEnd')" in vis_code
    assert (
        "y=alt.Y('yBinStart', type='quantitative', axis=alt.Axis(title='longitude'), bin = alt.BinParams(binned=True))"
        in vis_code
    )
    assert "y2=alt.Y2('yBinEnd')" in vis_code
    assert 'scale=alt.Scale(type="log")' in vis_code
    assert "chart.encode(color=alt.Color('availability_365',type='quantitative'))" in vis_code

    lux.config.plotting_backend = "matplotlib"
    vis = Vis(["price", "longitude", "availability_365"], df)
    vis_code = vis.to_matplotlib()
    assert "plt.imshow(df, cmap='viridis')" in vis_code
    assert "index='xBinStart'" in vis_code
    assert "values='availability_365'" in vis_code
    assert "columns='yBinStart'" in vis_code
    assert "plt.colorbar(label='availability_365')" in vis_code


def test_vegalite_default_actions_registered(global_var):
    df = pytest.car_df
    lux.config.plotting_backend = "vegalite"
    df._ipython_display_()
    # Histogram Chart
    assert "Distribution" in df.recommendation
    assert len(df.recommendation["Distribution"]) > 0

    # Occurrence Chart
    assert "Occurrence" in df.recommendation
    assert len(df.recommendation["Occurrence"]) > 0

    # Line Chart
    assert "Temporal" in df.recommendation
    assert len(df.recommendation["Temporal"]) > 0

    # Scatter Chart
    assert "Correlation" in df.recommendation
    assert len(df.recommendation["Correlation"]) > 0


def test_vegalite_default_actions_registered_2(global_var):
    import numpy as np

    df = pd.read_csv(
        "https://raw.githubusercontent.com/altair-viz/vega_datasets/master/vega_datasets/_data/airports.csv"
    )
    df["magnitude"] = np.random.randint(0, 20, size=len(df))
    lux.config.plotting_backend = "vegalite"

    # Choropleth Map
    assert "Geographical" in df.recommendation
    assert len(df.recommendation["Geographical"]) > 0

    # Occurrence Chart
    assert "Occurrence" in df.recommendation
    assert len(df.recommendation["Occurrence"]) > 0

    # Scatter Chart
    assert "Correlation" in df.recommendation
    assert len(df.recommendation["Correlation"]) > 0


def test_matplotlib_default_actions_registered(global_var):
    lux.config.plotting_backend = "matplotlib"
    df = pytest.car_df
    df._ipython_display_()
    # Histogram Chart
    assert "Distribution" in df.recommendation
    assert len(df.recommendation["Distribution"]) > 0

    # Occurrence Chart
    assert "Occurrence" in df.recommendation
    assert len(df.recommendation["Occurrence"]) > 0

    # Line Chart
    assert "Temporal" in df.recommendation
    assert len(df.recommendation["Temporal"]) > 0

    # Scatter Chart
    assert "Correlation" in df.recommendation
    assert len(df.recommendation["Correlation"]) > 0


def test_matplotlib_default_actions_registered_2(global_var):
    import numpy as np

    df = pd.read_csv(
        "https://raw.githubusercontent.com/altair-viz/vega_datasets/master/vega_datasets/_data/airports.csv"
    )
    df["magnitude"] = np.random.randint(0, 20, size=len(df))
    lux.config.plotting_backend = "matplotlib"

    # Choropleth Map
    assert "Geographical" in df.recommendation
    assert len(df.recommendation["Geographical"]) > 0

    # Occurrence Chart
    assert "Occurrence" in df.recommendation
    assert len(df.recommendation["Occurrence"]) > 0

    # Scatter Chart
    assert "Correlation" in df.recommendation
    assert len(df.recommendation["Correlation"]) > 0


def test_vegalite_heatmap_flag_config():
    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/airbnb_nyc.csv")
    lux.config.plotting_backend = "vegalite"
    df._ipython_display_()
    # Heatmap Chart
    assert df.recommendation["Correlation"][0]._postbin
    lux.config.heatmap = False
    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/airbnb_nyc.csv")
    df = df.copy()
    assert not df.recommendation["Correlation"][0]._postbin
    assert "Geographical" not in df.recommendation
    lux.config.heatmap = True


def test_matplotlib_heatmap_flag_config():
    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/airbnb_nyc.csv")
    lux.config.plotting_backend = "matplotlib"
    df._ipython_display_()
    # Heatmap Chart
    assert df.recommendation["Correlation"][0]._postbin
    lux.config.heatmap = False
    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/airbnb_nyc.csv")
    df = df.copy()
    assert not df.recommendation["Correlation"][0]._postbin
    lux.config.heatmap = True
    lux.config.plotting_backend = "vegalite"


def test_all_column_current_vis():
    df = pd.read_csv(
        "https://raw.githubusercontent.com/koldunovn/python_for_geosciences/master/DelhiTmax.txt",
        delimiter=r"\s+",
        parse_dates=[[0, 1, 2]],
        header=None,
    )
    df.columns = ["Date", "Temp"]
    df._ipython_display_()
    assert df.current_vis != None


def test_all_column_current_vis_filter():
    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    two_col_df = df[["Year", "Displacement"]]
    two_col_df._ipython_display_()
    assert two_col_df.current_vis != None
    assert two_col_df.current_vis[0]._all_column
    three_col_df = df[["Year", "Displacement", "Origin"]]
    three_col_df._ipython_display_()
    assert three_col_df.current_vis != None
    assert three_col_df.current_vis[0]._all_column


def test_intent_override_all_column():
    df = pytest.car_df
    df = df[["Year", "Displacement"]]
    df.intent = ["Year"]
    df._ipython_display_()
    current_vis_code = df.current_vis[0].to_altair()
    assert (
        "y = alt.Y('Record', type= 'quantitative', title='Number of Records'" in current_vis_code
    ), "All column not overriden by intent"
