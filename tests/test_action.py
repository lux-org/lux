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


def test_temporal_action(global_var):
    airbnb_df = pd.read_csv(
        "https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/airbnb_nyc.csv"
    )
    flights_df = pd.read_csv(
        "https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/flights.csv"
    )
    date_df = pd.DataFrame(
        {
            "date": [
                "2019-01",
                "2014-02",
                "2020-03",
                "2013-04",
                "2012-05",
                "2019-01",
                "2020-02",
                "2013-03",
                "2020-04",
                "2000-05",
                "2000-01",
                "2000-02",
                "2004-12",
                "2004-06",
                "2020-05",
                "2020-01",
                "2020-02",
                "2020-03",
                "2020-04",
                "2020-05",
            ]
        }
    )
    test_data = [airbnb_df, flights_df, date_df, pytest.car_df, pytest.olympic]
    test_data_vis_count = [4, 4, 2, 1, 1]
    for entry in zip(test_data, test_data_vis_count):
        df, num_vis = entry[0], entry[1]
        df._repr_html_()
        assert ("Temporal" in df.recommendation, "Temporal visualizations should be generated.")
        recommended = df.recommendation["Temporal"]
        assert (len(recommended) == num_vis, "Incorrect number of temporal visualizations generated.")
        temporal_col = [c for c in df.columns if df.data_type[c] == "temporal"]
        overall_vis = [
            vis.get_attr_by_channel("x")[0].attribute
            for vis in recommended
            if vis.score == 4 or vis.score == 5
        ]
        assert temporal_col.sort() == overall_vis.sort()


def test_vary_filter_val(global_var):
    lux.config.set_executor_type("Pandas")
    df = pytest.olympic
    vis = Vis(["Height", "SportType=Ball"], df)
    df.set_intent_as_vis(vis)
    df._ipython_display_()
    assert len(df.recommendation["Filter"]) == len(df["SportType"].unique()) - 1
    linechart = list(filter(lambda x: x.mark == "line", df.recommendation["Enhance"]))[0]
    assert (
        linechart.get_attr_by_channel("x")[0].attribute == "Year"
    ), "Ensure recommended vis does not inherit input vis channel"


def test_filter_inequality(global_var):
    df = pytest.car_df
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")

    df.set_intent(
        [
            lux.Clause(attribute="Horsepower"),
            lux.Clause(attribute="MilesPerGal"),
            lux.Clause(attribute="Acceleration", filter_op=">", value=10),
        ]
    )
    df._ipython_display_()

    from lux.utils.utils import get_filter_specs

    complement_vis = df.recommendation["Filter"][0]
    fltr_clause = get_filter_specs(complement_vis._intent)[0]
    assert fltr_clause.filter_op == "<="
    assert fltr_clause.value == 10


def test_generalize_action(global_var):
    # test that generalize action creates all unique visualizations
    df = pytest.car_df
    df["Year"] = pd.to_datetime(
        df["Year"], format="%Y"
    )  # change pandas dtype for the column "Year" to datetype
    df.set_intent(["Acceleration", "MilesPerGal", "Cylinders", "Origin=USA"])
    df._ipython_display_()
    assert len(df.recommendation["Generalize"]) == 4
    v1 = df.recommendation["Generalize"][0]
    v2 = df.recommendation["Generalize"][1]
    v3 = df.recommendation["Generalize"][2]
    v4 = df.recommendation["Generalize"][3]

    for clause in v4._inferred_intent:
        assert clause.value == ""  # No filter value
    assert v4.title == "Overall"

    check1 = v1 != v2 and v1 != v3 and v1 != v4
    check2 = v2 != v3 and v2 != v4
    check3 = v3 != v4
    assert check1 and check2 and check3


def test_row_column_group(global_var):
    df = pd.read_csv(
        "https://github.com/lux-org/lux-datasets/blob/master/data/state_timeseries.csv?raw=true"
    )
    df["Date"] = pd.to_datetime(df["Date"])
    tseries = df.pivot(index="State", columns="Date", values="Value")
    # Interpolating missing values
    tseries[tseries.columns.min()] = tseries[tseries.columns.min()].fillna(0)
    tseries[tseries.columns.max()] = tseries[tseries.columns.max()].fillna(tseries.max(axis=1))
    tseries = tseries.interpolate("zero", axis=1)
    tseries._ipython_display_()
    assert list(tseries.recommendation.keys()) == ["Temporal"]


def test_groupby(global_var):
    df = pytest.college_df
    groupbyResult = df.groupby("Region").sum()
    groupbyResult._ipython_display_()
    assert list(groupbyResult.recommendation.keys()) == ["Column Groups"]


def test_crosstab():
    # Example from http://www.datasciencemadesimple.com/cross-tab-cross-table-python-pandas/
    d = {
        "Name": [
            "Alisa",
            "Bobby",
            "Cathrine",
            "Alisa",
            "Bobby",
            "Cathrine",
            "Alisa",
            "Bobby",
            "Cathrine",
            "Alisa",
            "Bobby",
            "Cathrine",
        ],
        "Exam": [
            "Semester 1",
            "Semester 1",
            "Semester 1",
            "Semester 1",
            "Semester 1",
            "Semester 1",
            "Semester 2",
            "Semester 2",
            "Semester 2",
            "Semester 2",
            "Semester 2",
            "Semester 2",
        ],
        "Subject": [
            "Mathematics",
            "Mathematics",
            "Mathematics",
            "Science",
            "Science",
            "Science",
            "Mathematics",
            "Mathematics",
            "Mathematics",
            "Science",
            "Science",
            "Science",
        ],
        "Result": [
            "Pass",
            "Pass",
            "Fail",
            "Pass",
            "Fail",
            "Pass",
            "Pass",
            "Fail",
            "Fail",
            "Pass",
            "Pass",
            "Fail",
        ],
    }

    df = pd.DataFrame(d, columns=["Name", "Exam", "Subject", "Result"])
    result = pd.crosstab([df.Exam], df.Result)
    result._ipython_display_()
    assert list(result.recommendation.keys()) == ["Row Groups", "Column Groups"]


def test_custom_aggregation(global_var):
    import numpy as np

    df = pytest.college_df
    df.set_intent(["HighestDegree", lux.Clause("AverageCost", aggregation=np.ptp)])
    df._ipython_display_()
    assert list(df.recommendation.keys()) == ["Enhance", "Filter", "Generalize"]
    df.clear_intent()


def test_year_filter_value(global_var):
    df = pytest.car_df
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df.set_intent(["Acceleration", "Horsepower"])
    df._ipython_display_()
    list_of_vis_with_year_filter = list(
        filter(
            lambda vis: len(
                list(
                    filter(
                        lambda clause: clause.value != "" and clause.attribute == "Year",
                        vis._intent,
                    )
                )
            )
            != 0,
            df.recommendation["Filter"],
        )
    )
    vis = list_of_vis_with_year_filter[0]
    assert (
        "T00:00:00.000000000" not in vis.to_altair()
    ), "Year filter title contains extraneous string, not displayed as summarized string"
    df.clear_intent()


def test_similarity(global_var):
    lux.config.early_pruning = False
    df = pytest.car_df
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df.set_intent(
        [
            lux.Clause("Year", channel="x"),
            lux.Clause("Displacement", channel="y"),
            lux.Clause("Origin=USA"),
        ]
    )
    df._ipython_display_()
    assert len(df.recommendation["Similarity"]) == 2
    ranked_list = df.recommendation["Similarity"]

    japan_vis = list(
        filter(
            lambda vis: vis.get_attr_by_attr_name("Origin")[0].value == "Japan",
            ranked_list,
        )
    )[0]
    europe_vis = list(
        filter(
            lambda vis: vis.get_attr_by_attr_name("Origin")[0].value == "Europe",
            ranked_list,
        )
    )[0]
    assert japan_vis.score > europe_vis.score
    df.clear_intent()
    lux.config.early_pruning = True


def test_similarity2():
    df = pd.read_csv(
        "https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/real_estate_tutorial.csv"
    )

    df["Month"] = pd.to_datetime(df["Month"], format="%m")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")

    df.intent = [
        lux.Clause("Year"),
        lux.Clause("PctForeclosured"),
        lux.Clause("City=Crofton"),
    ]

    ranked_list = df.recommendation["Similarity"]

    morrisville_vis = list(
        filter(
            lambda vis: vis.get_attr_by_attr_name("City")[0].value == "Morrisville",
            ranked_list,
        )
    )[0]
    watertown_vis = list(
        filter(
            lambda vis: vis.get_attr_by_attr_name("City")[0].value == "Watertown",
            ranked_list,
        )
    )[0]
    assert morrisville_vis.score > watertown_vis.score


def test_intent_retained():
    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/employee.csv")
    df.intent = ["Attrition"]
    df._ipython_display_()

    df["%WorkingYearsAtCompany"] = df["YearsAtCompany"] / df["TotalWorkingYears"]
    assert df.current_vis != None
    assert df.intent != None
    assert df._recs_fresh == False
    assert df._metadata_fresh == False

    df._ipython_display_()
    assert list(df.recommendation.keys()) == ["Enhance", "Filter"]


def test_metadata_propogate_invalid_intent():
    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/employee.csv")
    df.intent = ["Attrition"]
    new_df = df.groupby("BusinessTravel").mean()
    assert new_df.intent[0].attribute == "Attrition", "User-specified intent is retained"
    assert new_df._inferred_intent == [], "Invalid inferred intent is cleared"
    new_df._ipython_display_()
    assert new_df.current_vis == []
