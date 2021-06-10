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
import numpy as np
import warnings

###################
# DataFrame Tests #
###################


def test_deepcopy(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df._ipython_display_()
    saved_df = df.copy(deep=True)
    saved_df._ipython_display_()
    check_metadata_equal(df, saved_df)


def test_rename_inplace(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df._ipython_display_()
    new_df = df.copy(deep=True)
    df.rename(columns={"Name": "Car Name"}, inplace=True)
    df._ipython_display_()
    new_df._ipython_display_()
    # new_df is the old dataframe (df) with the new column name changed inplace
    new_df, df = df, new_df

    assert df.data_type != new_df.data_type

    assert df.data_type["Name"] == new_df.data_type["Car Name"]

    inverted_data_type = lux.config.executor.invert_data_type(df.data_type)
    new_inverted_data_type = lux.config.executor.invert_data_type(new_df.data_type)

    assert inverted_data_type != new_inverted_data_type

    assert inverted_data_type["nominal"][0] == "Name"
    assert new_inverted_data_type["nominal"][0] == "Car Name"

    data_model_lookup = lux.config.executor.compute_data_model_lookup(df.data_type)
    new_data_model_lookup = lux.config.executor.compute_data_model_lookup(new_df.data_type)

    assert data_model_lookup != new_data_model_lookup

    assert data_model_lookup["Name"] == new_data_model_lookup["Car Name"]

    data_model = lux.config.executor.compute_data_model(df.data_type)
    new_data_model = lux.config.executor.compute_data_model(new_df.data_type)

    assert data_model != new_data_model

    assert data_model["dimension"][0] == "Name"
    assert new_data_model["dimension"][0] == "Car Name"

    assert list(df.unique_values.values()) == list(new_df.unique_values.values())
    assert list(df.cardinality.values()) == list(new_df.cardinality.values())
    assert df._min_max == new_df._min_max
    assert df.pre_aggregated == new_df.pre_aggregated


def test_rename(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df._ipython_display_()
    new_df = df.rename(columns={"Name": "Car Name"}, inplace=False)
    new_df._ipython_display_()
    assert df.data_type != new_df.data_type

    assert df.data_type["Name"] == new_df.data_type["Car Name"]

    inverted_data_type = lux.config.executor.invert_data_type(df.data_type)
    new_inverted_data_type = lux.config.executor.invert_data_type(new_df.data_type)

    assert inverted_data_type != new_inverted_data_type

    assert inverted_data_type["nominal"][0] == "Name"
    assert new_inverted_data_type["nominal"][0] == "Car Name"

    data_model_lookup = lux.config.executor.compute_data_model_lookup(df.data_type)
    new_data_model_lookup = lux.config.executor.compute_data_model_lookup(new_df.data_type)

    assert data_model_lookup != new_data_model_lookup

    assert data_model_lookup["Name"] == new_data_model_lookup["Car Name"]

    data_model = lux.config.executor.compute_data_model(df.data_type)
    new_data_model = lux.config.executor.compute_data_model(new_df.data_type)

    assert data_model != new_data_model

    assert data_model["dimension"][0] == "Name"
    assert new_data_model["dimension"][0] == "Car Name"

    assert list(df.unique_values.values()) == list(new_df.unique_values.values())
    assert list(df.cardinality.values()) == list(new_df.cardinality.values())
    assert df._min_max == new_df._min_max
    assert df.pre_aggregated == new_df.pre_aggregated


def test_rename3(global_var):

    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df.columns = [
        "col1",
        "col2",
        "col3",
        "col4",
        "col5",
        "col6",
        "col7",
        "col8",
        "col9",
        "col10",
    ]
    df._ipython_display_()
    assert list(df.recommendation.keys()) == [
        "Correlation",
        "Distribution",
        "Occurrence",
        "Temporal",
    ]
    assert len(df.cardinality) == 10
    assert "col2" in list(df.cardinality.keys())


def test_concat(global_var):

    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    new_df = pd.concat([df.loc[:, "Name":"Cylinders"], df.loc[:, "Year":"Origin"]], axis="columns")
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == [
        "Distribution",
        "Occurrence",
        "Temporal",
    ]
    assert len(new_df.cardinality) == 5


def test_groupby_agg(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    new_df = df.groupby("Year").agg(sum)
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == ["Column Groups"]
    assert len(new_df.cardinality) == 7


def test_groupby_agg_big(global_var):
    df = pd.read_csv("lux/data/car.csv")
    new_df = df.groupby("Brand").agg(sum)
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == ["Column Groups"]
    assert len(new_df.cardinality) == 8
    year_vis = list(
        filter(
            lambda vis: vis.get_attr_by_attr_name("Year") != [],
            new_df.recommendation["Column Groups"],
        )
    )[0]
    assert year_vis.mark == "bar"
    assert year_vis.get_attr_by_channel("x")[0].attribute == "Year"
    new_df = new_df.T
    new_df._ipython_display_()
    year_vis = list(
        filter(
            lambda vis: vis.get_attr_by_attr_name("Year") != [],
            new_df.recommendation["Row Groups"],
        )
    )[0]
    assert year_vis.mark == "bar"
    assert year_vis.get_attr_by_channel("x")[0].attribute == "Year"


def test_qcut(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df["Weight"] = pd.qcut(df["Weight"], q=3)
    df._ipython_display_()


def test_cut(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Weight"] = pd.cut(df["Weight"], bins=[0, 2500, 7500, 10000], labels=["small", "medium", "large"])
    df._ipython_display_()


def test_groupby_agg_very_small(global_var):

    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    new_df = df.groupby("Origin").agg(sum).reset_index()
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == ["Column Groups"]
    assert len(new_df.cardinality) == 7


# def test_groupby_multi_index(global_var):
#     url = 'https://github.com/lux-org/lux-datasets/blob/master/data/cars.csv?raw=true'
#     df = pd.read_csv(url)
#     df["Year"] = pd.to_datetime(df["Year"], format='%Y')
#     new_df = df.groupby(["Year", "Cylinders"]).agg(sum).stack().reset_index()
#     new_df._ipython_display_()
#     assert list(new_df.recommendation.keys() ) == ['Column Groups'] # TODO
#     assert len(new_df.cardinality) == 7 # TODO


def test_query(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    new_df = df.query("Weight > 3000")
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == [
        "Correlation",
        "Distribution",
        "Occurrence",
        "Temporal",
    ]
    assert len(new_df.cardinality) == 10


def test_pop(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df.pop("Weight")
    df._ipython_display_()
    assert list(df.recommendation.keys()) == [
        "Correlation",
        "Distribution",
        "Occurrence",
        "Temporal",
    ]
    assert len(df.cardinality) == 9


def test_transform(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    new_df = df.iloc[:, 1:].groupby("Origin").transform(sum)
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == ["Occurrence"]
    assert len(new_df.cardinality) == 7


def test_get_group(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    gbobj = df.groupby("Origin")
    new_df = gbobj.get_group("Japan")
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == [
        "Correlation",
        "Distribution",
        "Occurrence",
        "Temporal",
    ]
    assert len(new_df.cardinality) == 10


def test_applymap(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    mapping = {"USA": 0, "Europe": 1, "Japan": 2}
    df["Origin"] = df[["Origin"]].applymap(mapping.get)
    df._ipython_display_()
    assert list(df.recommendation.keys()) == [
        "Correlation",
        "Distribution",
        "Occurrence",
        "Temporal",
    ]
    assert len(df.cardinality) == 10


def test_strcat(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df["combined"] = df["Origin"].str.cat(df["Brand"], sep=", ")
    df._ipython_display_()
    assert list(df.recommendation.keys()) == [
        "Correlation",
        "Distribution",
        "Occurrence",
        "Temporal",
    ]
    assert len(df.cardinality) == 11


def test_named_agg(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    new_df = df.groupby("Brand").agg(
        avg_weight=("Weight", "mean"),
        max_weight=("Weight", "max"),
        mean_displacement=("Displacement", "mean"),
    )
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == ["Column Groups"]
    assert len(new_df.cardinality) == 4


def test_change_dtype(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    df["Cylinders"] = pd.Series(df["Cylinders"], dtype="Int64")
    df._ipython_display_()
    assert list(df.recommendation.keys()) == [
        "Correlation",
        "Distribution",
        "Occurrence",
        "Temporal",
    ]
    assert len(df.data_type) == 10


def test_get_dummies(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    new_df = pd.get_dummies(df)
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == [
        "Correlation",
        "Distribution",
        "Occurrence",
        "Temporal",
    ]
    assert len(new_df.data_type) == 339


def test_drop(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    new_df = df.drop([0, 1, 2], axis="rows")
    new_df2 = new_df.drop(["Name", "MilesPerGal", "Cylinders"], axis="columns")
    new_df2._ipython_display_()
    assert list(new_df2.recommendation.keys()) == [
        "Correlation",
        "Distribution",
        "Occurrence",
        "Temporal",
    ]
    assert len(new_df2.cardinality) == 7


def test_merge(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    new_df = df.drop([0, 1, 2], axis="rows")
    new_df2 = pd.merge(df, new_df, how="left", indicator=True)
    new_df2._ipython_display_()
    assert list(new_df2.recommendation.keys()) == [
        "Correlation",
        "Distribution",
        "Occurrence",
        "Temporal",
    ]  # TODO once bug is fixed
    assert len(new_df2.cardinality) == 11


def test_prefix(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    new_df = df.add_prefix("1_")
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == [
        "Correlation",
        "Distribution",
        "Occurrence",
        "Temporal",
    ]
    assert len(new_df.cardinality) == 10
    assert new_df.cardinality["1_Name"] == 300


def test_loc(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    new_df = df.loc[:, "Displacement":"Origin"]
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == [
        "Correlation",
        "Distribution",
        "Occurrence",
        "Temporal",
    ]
    assert len(new_df.cardinality) == 6
    new_df = df.loc[0:10, "Displacement":"Origin"]
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == [
        "Correlation",
        "Distribution",
        "Occurrence",
        "Temporal",
    ]
    assert len(new_df.cardinality) == 6
    new_df = df.loc[0:10, "Displacement":"Horsepower"]
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == ["Correlation", "Distribution"]
    assert len(new_df.cardinality) == 2
    import numpy as np

    inter_df = df.groupby("Brand")[["Acceleration", "Weight", "Horsepower"]].agg(np.mean)
    new_df = inter_df.loc["chevrolet":"fiat", "Acceleration":"Weight"]
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == ["Column Groups"]
    assert len(new_df.cardinality) == 3


def test_iloc(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")
    new_df = df.iloc[:, 3:9]
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == [
        "Correlation",
        "Distribution",
        "Occurrence",
        "Temporal",
    ]
    assert len(new_df.cardinality) == 6
    new_df = df.iloc[0:11, 3:9]
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == [
        "Correlation",
        "Distribution",
        "Occurrence",
        "Temporal",
    ]
    assert len(new_df.cardinality) == 6
    new_df = df.iloc[0:11, 3:5]
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == ["Correlation", "Distribution"]
    assert len(new_df.cardinality) == 2
    import numpy as np

    inter_df = df.groupby("Brand")[["Acceleration", "Weight", "Horsepower"]].agg(np.mean)
    new_df = inter_df.iloc[5:10, 0:2]
    new_df._ipython_display_()
    assert list(new_df.recommendation.keys()) == ["Column Groups"]
    assert len(new_df.cardinality) == 3


def check_metadata_equal(df1, df2):
    # Checks to make sure metadata for df1 and df2 are equal.
    for attr in df1._metadata:
        if attr == "_recommendation":
            x = df1._recommendation
            y = df2._recommendation
            for key in x:
                if key in y:
                    assert len(x[key]) == len(y[key])
                    for i in range(len(x[key])):
                        vis1 = x[key][i]
                        vis2 = y[key][i]
                        compare_vis(vis1, vis2)
        elif attr == "_rec_info":
            x = df1._rec_info
            y = df2._rec_info
            assert len(x) == len(y)
            for i in range(len(x)):
                x_info, y_info = x[i], y[i]
                for key in x_info:
                    if key in y_info and key == "collection":
                        assert len(x_info[key]) == len(y_info[key])
                        for i in range(len(x_info[key])):
                            vis1 = x_info[key][i]
                            vis2 = y_info[key][i]
                            compare_vis(vis1, vis2)
                    elif key in y_info:
                        assert x_info[key] == y_info[key]

        elif attr != "_widget" and attr != "_sampled" and attr != "_message":
            assert getattr(df1, attr) == getattr(df2, attr)


def compare_clauses(clause1, clause2):
    assert clause1.description == clause2.description
    assert clause1.attribute == clause2.attribute
    assert clause1.value == clause2.value
    assert clause1.filter_op == clause2.filter_op
    assert clause1.channel == clause2.channel
    assert clause1.data_type == clause2.data_type
    assert clause1.data_model == clause2.data_model
    assert clause1.bin_size == clause2.bin_size
    assert clause1.weight == clause2.weight
    assert clause1.sort == clause2.sort
    assert clause1.exclude == clause2.exclude


def compare_vis(vis1, vis2):
    assert len(vis1._intent) == len(vis2._intent)
    for j in range(len(vis1._intent)):
        compare_clauses(vis1._intent[j], vis2._intent[j])
    assert len(vis1._inferred_intent) == len(vis2._inferred_intent)
    for j in range(len(vis1._inferred_intent)):
        compare_clauses(vis1._inferred_intent[j], vis2._inferred_intent[j])
    compare_df(vis1._source, vis2._source)
    assert vis1._code == vis2._code
    assert vis1._mark == vis2._mark
    assert vis1._min_max == vis2._min_max
    assert vis1.title == vis2.title
    assert vis1.score == vis2.score


def compare_df(df1, df2):
    if df1 is not None and df2 is not None:
        assert df1.head().to_dict() == df2.head().to_dict()


def test_index(global_var):
    # testing set_index and reset_index functions
    # setting a column as an index should remove it from the dataframe's column list
    # and change the dataframe's index name parameter
    df = pd.read_csv("lux/data/car.csv")
    df["Year"] = pd.to_datetime(df["Year"], format="%Y")

    df = df.set_index(["Name"])
    # if this assert fails, then the index column has not properly been removed from the dataframe's column and registered as an index
    assert "Name" not in df.columns and df.index.name == "Name"
    df._ipython_display_()
    assert len(df.recommendation) > 0
    df = df.reset_index()
    assert "Name" in df.columns and df.index.name != "Name"
    df._ipython_display_()
    assert len(df.recommendation) > 0

    df.set_index(["Name"], inplace=True)
    assert "Name" not in df.columns and df.index.name == "Name"
    df._ipython_display_()
    assert len(df.recommendation) > 0
    df.reset_index(inplace=True)
    assert "Name" in df.columns and df.index.name != "Name"
    df._ipython_display_()
    assert len(df.recommendation) > 0

    df = df.set_index(["Name"])
    assert "Name" not in df.columns and df.index.name == "Name"
    df._ipython_display_()
    assert len(df.recommendation) > 0
    df = df.reset_index(drop=True)
    assert "Name" not in df.columns and df.index.name != "Name"
    df._ipython_display_()
    assert len(df.recommendation) > 0


def test_index_col(global_var):
    df = pd.read_csv("lux/data/car.csv", index_col="Name")
    # if this assert fails, then the index column has not properly been removed from the dataframe's column and registered as an index
    assert "Name" not in df.columns and df.index.name == "Name"
    df._ipython_display_()
    assert len(df.recommendation) > 0
    df = df.reset_index()
    assert "Name" in df.columns and df.index.name != "Name"
    df._ipython_display_()
    assert len(df.recommendation) > 0

    # this case is not yet addressed, need to have a check that eliminates bar charts with duplicate column names
    # df = df.set_index(["Name"], drop=False)
    # assert "Name" not in df.columns and df.index.name == "Name"
    # df._ipython_display_()
    # assert len(df.recommendation) > 0
    # df = df.reset_index(drop=True)
    # assert "Name" not in df.columns and df.index.name != "Name"


################
# Series Tests #
################


def test_df_to_series(global_var):
    # Ensure metadata is kept when going from df to series
    df = pd.read_csv("lux/data/car.csv")
    df._ipython_display_()  # compute metadata
    assert df.cardinality is not None
    series = df["Weight"]
    assert isinstance(series, lux.core.series.LuxSeries), "Derived series is type LuxSeries."
    df["Weight"]._metadata
    assert (
        df["Weight"]._metadata == pytest.metadata
    ), "Metadata is lost when going from Dataframe to Series."
    assert df.cardinality is not None, "Metadata is lost when going from Dataframe to Series."
    assert series.name == "Weight", "Pandas Series original `name` property not retained."


def test_value_counts(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df._ipython_display_()  # compute metadata
    assert df.cardinality is not None
    series = df["Weight"]
    series.value_counts()
    assert type(df["Brand"].value_counts()) == lux.core.series.LuxSeries
    assert (
        df["Weight"]._metadata == pytest.metadata
    ), "Metadata is lost when going from Dataframe to Series."
    assert df.cardinality is not None, "Metadata is lost when going from Dataframe to Series."
    assert series.name == "Weight", "Pandas Series original `name` property not retained."


def test_str_replace(global_var):
    df = pd.read_csv("lux/data/car.csv")
    df._ipython_display_()  # compute metadata
    assert df.cardinality is not None
    series = df["Brand"].str.replace("chevrolet", "chevy")
    assert isinstance(series, lux.core.series.LuxSeries), "Derived series is type LuxSeries."
    assert (
        df["Brand"]._metadata == pytest.metadata
    ), "Metadata is lost when going from Dataframe to Series."
    assert df.cardinality is not None, "Metadata is lost when going from Dataframe to Series."
    assert series.name == "Brand", "Pandas Series original `name` property not retained."


################
# Read Tests #
################


def test_read_json(global_var):
    url = "https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/car.json"
    df = pd.read_json(url)
    df._ipython_display_()
    assert list(df.recommendation.keys()) == [
        "Correlation",
        "Distribution",
        "Occurrence",
        "Temporal",
    ]
    assert len(df.data_type) == 10


def test_read_sas(global_var):
    url = "https://github.com/lux-org/lux-datasets/blob/master/data/airline.sas7bdat?raw=true"
    df = pd.read_sas(url, format="sas7bdat")
    df._ipython_display_()
    assert list(df.recommendation.keys()) == ["Correlation", "Distribution", "Temporal"]
    assert len(df.data_type) == 6


def test_read_multi_dtype(global_var):
    url = "https://github.com/lux-org/lux-datasets/blob/master/data/car-data.xls?raw=true"
    df = pd.read_excel(url)
    with pytest.warns(UserWarning, match="mixed type") as w:
        df._ipython_display_()
        assert "df['Car Type'] = df['Car Type'].astype(str)" in str(w[-1].message)
