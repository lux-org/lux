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


def test_vary_filter_val(global_var):
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
        "T00:00:00.000000000" not in vis.to_Altair()
    ), "Year filter title contains extraneous string, not displayed as summarized string"
    df.clear_intent()


def test_similarity(global_var):
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

def test_all_column_current_vis():
    df = pd.read_csv('https://raw.githubusercontent.com/koldunovn/python_for_geosciences/master/DelhiTmax.txt', delimiter=r"\s+", parse_dates=[[0,1,2]], header=None)
    df.columns = ['Date', 'Temp']
    df._ipython_display_()
    assert df.current_vis != None

    df = pd.DataFrame({'nPts': {0: 49999, 1: 71174, 2: 101317, 3: 144224, 4: 205303, 5: 292249, 6: 416016, 7: 592198, 8: 842993, 9: 1200000}, 't_heatmap': {0: 0.15121674537658691, 1: 0.1811518669128418, 2: 0.2179429531097412, 3: 0.2787730693817139, 4: 0.3973350524902344, 5: 0.4233138561248779, 6: 0.580251932144165, 7: 0.7928099632263184, 8: 1.0876789093017578, 9: 1.6242818832397459}, 't_color_heatmap': {0: 0.14242982864379886, 1: 0.18866705894470212, 2: 0.1566781997680664, 3: 0.16737699508666992, 4: 0.19900894165039065, 5: 0.2701129913330078, 6: 0.2533812522888184, 7: 0.37183785438537603, 8: 0.3830866813659668, 9: 0.39321017265319824}, 't_bar': {0: 0.01940608024597168, 1: 0.02618718147277832, 2: 0.024693727493286133, 3: 0.029685020446777344, 4: 0.03471803665161133, 5: 0.04173588752746582, 6: 0.04706382751464844, 7: 0.0667569637298584, 8: 0.08260798454284668, 9: 0.1006929874420166}, 't_cbar': {0: 0.04185795783996582, 1: 0.050965070724487305, 2: 0.052091121673583984, 3: 0.0610501766204834, 4: 0.07504606246948242, 5: 0.09924101829528807, 6: 0.10392117500305176, 7: 0.13044309616088867, 8: 0.18137121200561526, 9: 0.2069528102874756}, 't_hist': {0: 0.01846003532409668, 1: 0.018136978149414062, 2: 0.018748998641967773, 3: 0.01876473426818848, 4: 0.02434706687927246, 5: 0.025368213653564453, 6: 0.02530217170715332, 7: 0.02823114395141602, 8: 0.029034852981567383, 9: 0.034781217575073235}, 't_scatter': {0: 0.8179378509521484, 1: 1.0982017517089844, 2: 1.4875690937042236, 3: 2.146117925643921, 4: 3.1123709678649902, 5: 3.92416787147522, 6: 6.097048044204713, 7: 8.803220987319945, 8: 12.054464101791382, 9: 17.740845680236816}, 't_color_scatter': {0: 1.3474130630493164, 1: 1.7953579425811768, 2: 2.6268541812896733, 3: 3.646371126174927, 4: 4.901940107345581, 5: 6.974237203598023, 6: 10.197483777999876, 7: 14.134275913238525, 8: 21.13951110839844, 9: 27.127063989639282}})
    df = df.melt(id_vars=["nPts"],value_vars=['t_heatmap', 't_color_heatmap', 't_bar', 't_cbar', 't_hist','t_scatter', 't_color_scatter'], var_name="type", value_name='t')
    df._ipython_display_()
    assert df.current_vis != None
