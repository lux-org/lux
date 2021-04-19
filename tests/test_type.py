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
import random
import pandas as pd
import warnings


# Suite of test that checks if data_type inferred correctly by Lux
def test_check_cars():
    lux.config.set_SQL_connection("")
    df = pd.read_csv("lux/data/car.csv")
    df.maintain_metadata()
    assert df.data_type["Name"] == "nominal"
    assert df.data_type["MilesPerGal"] == "quantitative"
    assert df.data_type["Cylinders"] == "nominal"
    assert df.data_type["Displacement"] == "quantitative"
    assert df.data_type["Horsepower"] == "quantitative"
    assert df.data_type["Weight"] == "quantitative"
    assert df.data_type["Acceleration"] == "quantitative"
    assert df.data_type["Year"] == "temporal"
    assert df.data_type["Origin"] == "nominal"


def test_check_int_id():
    df = pd.read_csv(
        "https://github.com/lux-org/lux-datasets/blob/master/data/instacart_sample.csv?raw=true"
    )
    df._ipython_display_()
    inverted_data_type = lux.config.executor.invert_data_type(df.data_type)
    assert len(inverted_data_type["id"]) == 3
    assert (
        "<code>order_id</code>, <code>product_id</code>, <code>user_id</code> is not visualized since it resembles an ID field."
        in df._message.to_html()
    )


def test_check_str_id():
    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/churn.csv?raw=true")
    df._ipython_display_()
    assert (
        "<code>customerID</code> is not visualized since it resembles an ID field.</li>"
        in df._message.to_html()
    )


def test_check_hpi():
    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/hpi.csv?raw=true")
    df.maintain_metadata()

    assert df.data_type == {
        "HPIRank": "quantitative",
        "Country": "geographical",
        "SubRegion": "nominal",
        "AverageLifeExpectancy": "quantitative",
        "AverageWellBeing": "quantitative",
        "HappyLifeYears": "quantitative",
        "Footprint": "quantitative",
        "InequalityOfOutcomes": "quantitative",
        "InequalityAdjustedLifeExpectancy": "quantitative",
        "InequalityAdjustedWellbeing": "quantitative",
        "HappyPlanetIndex": "quantitative",
        "GDPPerCapita": "quantitative",
        "Population": "quantitative",
    }


def test_check_airbnb():
    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/airbnb_nyc.csv?raw=true")
    df.maintain_metadata()
    assert df.data_type == {
        "id": "id",
        "name": "nominal",
        "host_id": "id",
        "host_name": "nominal",
        "neighbourhood_group": "nominal",
        "neighbourhood": "nominal",
        "latitude": "quantitative",
        "longitude": "quantitative",
        "room_type": "nominal",
        "price": "quantitative",
        "minimum_nights": "quantitative",
        "number_of_reviews": "quantitative",
        "last_review": "temporal",
        "reviews_per_month": "quantitative",
        "calculated_host_listings_count": "quantitative",
        "availability_365": "quantitative",
    }


def test_check_airports():
    df = pd.read_csv(
        "https://raw.githubusercontent.com/altair-viz/vega_datasets/master/vega_datasets/_data/airports.csv"
    )
    df.maintain_metadata()
    assert df.data_type == {
        "iata": "id",
        "name": "nominal",
        "city": "nominal",
        "state": "geographical",
        "country": "geographical",
        "latitude": "quantitative",
        "longitude": "quantitative",
    }


def test_check_datetime():
    df = pd.DataFrame(
        {
            "a": ["2020-01-01"],
            "b": ["20-01-01"],
            "c": ["20-jan-01"],
            "d": ["20-january-01"],
            "e": ["2020 January 01"],
            "f": ["2020 January 01 00:00:00 pm PT"],
            "g": ["2020 January 01 13:00:00"],
            "h": ["2020 January 01 23:59:59 GTC-6"],
        }
    )
    df.maintain_metadata()
    assert df.data_type == {
        "a": "temporal",
        "b": "temporal",
        "c": "temporal",
        "d": "temporal",
        "e": "temporal",
        "f": "temporal",
        "g": "temporal",
        "h": "temporal",
    }


def test_check_datetime_numeric_values():
    car_df = pd.read_csv("lux/data/car.csv")
    car_df = car_df.rename(columns={"Year": "blah"})
    car_df.maintain_metadata()
    assert car_df.data_type["blah"] == "temporal"

    spotify_df = pd.read_csv(
        "https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/spotify.csv"
    )
    spotify_df = spotify_df.rename(columns={"year": "blah"})
    spotify_df.maintain_metadata()
    assert spotify_df.data_type["blah"] == "temporal"
    assert spotify_df.data_type["release_date"] == "temporal"


def test_check_stock():
    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/stocks.csv?raw=true")
    df.maintain_metadata()
    assert df.data_type == {
        "symbol": "nominal",
        "monthdate": "temporal",
        "price": "quantitative",
    }, "Stock dataset type detection error"


def test_check_college():
    df = pd.read_csv("lux/data/college.csv")
    df.maintain_metadata()
    assert df.data_type == {
        "Name": "nominal",
        "PredominantDegree": "nominal",
        "HighestDegree": "nominal",
        "FundingModel": "nominal",
        "Region": "nominal",
        "Geography": "nominal",
        "AdmissionRate": "quantitative",
        "ACTMedian": "quantitative",
        "SATAverage": "quantitative",
        "AverageCost": "quantitative",
        "Expenditure": "quantitative",
        "AverageFacultySalary": "quantitative",
        "MedianDebt": "quantitative",
        "AverageAgeofEntry": "quantitative",
        "MedianFamilyIncome": "quantitative",
        "MedianEarnings": "quantitative",
    }


def test_float_categorical():
    values = [
        {"A": 6.0, "B": 1.0, "C": 1.0, "D": 3.0, "E": 2.0, "F": 5.0},
        {"A": 5.0, "B": 2.0, "C": 2.0, "D": 2.0, "E": 2.0, "F": 3.0},
        {"A": 3.0, "B": 6.0, "C": 3.0, "D": 3.0, "E": 2.0, "F": 5.0},
        {"A": 6.0, "B": 3.0, "C": 3.0, "D": 2.0, "E": 2.0, "F": 2.0},
        {"A": 7.0, "B": 4.0, "C": 2.0, "D": 2.0, "E": 2.0, "F": 4.0},
        {"A": 5.0, "B": 3.0, "C": 6.0, "D": 3.0, "E": 3.0, "F": 4.0},
        {"A": 3.0, "B": 4.0, "C": 3.0, "D": 6.0, "E": 5.0, "F": 5.0},
        {"A": 3.0, "B": 3.0, "C": 2.0, "D": 2.0, "E": 4.0, "F": 5.0},
        {"A": 3.0, "B": 2.0, "C": 2.0, "D": 2.0, "E": 2.0, "F": 4.0},
        {"A": 1.0, "B": 2.0, "C": 2.0, "D": 2.0, "E": 2.0, "F": 6.0},
        {"A": 3.0, "B": 3.0, "C": 2.0, "D": 3.0, "E": 3.0, "F": 5.0},
        {"A": 7.0, "B": 1.0, "C": 1.0, "D": 2.0, "E": 2.0, "F": 3.0},
        {"A": 6.0, "B": 2.0, "C": 2.0, "D": 2.0, "E": 2.0, "F": 3.0},
        {"A": 2.0, "B": 3.0, "C": 2.0, "D": 3.0, "E": 3.0, "F": 4.0},
        {"A": 6.0, "B": 2.0, "C": 3.0, "D": 3.0, "E": 3.0, "F": 5.0},
    ]
    df = pd.DataFrame(values)
    df.maintain_metadata()
    inverted_data_type = lux.config.executor.invert_data_type(df.data_type)
    assert inverted_data_type["nominal"] == [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
    ], "Float column should be detected as categorical"
    for x in list(df.dtypes):
        assert x == "float64", "Source dataframe preserved as float dtype"


def test_set_data_type():
    df = pd.read_csv(
        "https://github.com/lux-org/lux-datasets/blob/master/data/real_estate_tutorial.csv?raw=true"
    )
    with pytest.warns(UserWarning) as w:
        df._ipython_display_()
        assert "starter template that you can use" in str(w[-1].message)
        assert "df.set_data_type" in str(w[-1].message)

    df.set_data_type({"Month": "nominal", "Year": "nominal"})
    assert df.data_type["Month"] == "nominal"
    assert df.data_type["Year"] == "nominal"
    with warnings.catch_warnings() as w:
        warnings.simplefilter("always")
        df._ipython_display_()
        assert not w


def test_set_data_type_invalid():
    df = pd.read_csv(
        "https://github.com/lux-org/lux-datasets/blob/master/data/real_estate_tutorial.csv?raw=true"
    )
    with pytest.raises(ValueError):
        df.set_data_type({"Month": "nomnal", "Year": "nomnal"})


def test_set_wrong_data_type():
    df = pd.read_csv(
        "https://github.com/lux-org/lux-datasets/blob/master/data/real_estate_tutorial.csv?raw=true"
    )
    df.set_data_type({"Year": "quantitative"})
    assert df.data_type["Year"] == "quantitative"


def test_id_with_label():
    df = pd.read_csv(
        "https://github.com/lux-org/lux-datasets/blob/master/data/state_timeseries.csv?raw=true"
    )
    df.maintain_metadata()
    assert df.data_type == {"Date": "temporal", "State": "geographical", "Value": "quantitative"}


def test_ID_random():
    """Tests whether a ID column not satisfying other properties of an ID gets recognized."""
    values = [
        {"ID": random.randint(0, 1000), "A": 6.0, "B": 1.0, "C": 1.0, "D": 3.0, "E": 2.0, "F": 5.0}
        for x in range(1000)
    ]
    df = pd.DataFrame(values)
    df.maintain_metadata()
    assert df.data_type == {
        "ID": "quantitative",
        "A": "nominal",
        "B": "nominal",
        "C": "nominal",
        "D": "nominal",
        "E": "nominal",
        "F": "nominal",
    }


def test_ID():
    """Tests different ways of writing id"""
    values = [{"ID": x, "A": 6.0, "B": 1.0, "C": 1.0, "D": 3.0, "E": 2.0, "F": 5.0} for x in range(1000)]
    df = pd.DataFrame(values)
    df.maintain_metadata()
    assert df.data_type == {
        "ID": "id",
        "A": "nominal",
        "B": "nominal",
        "C": "nominal",
        "D": "nominal",
        "E": "nominal",
        "F": "nominal",
    }


def test_id_aug_test():
    """Tests in a different dataset
    Reference: https://www.kaggle.com/arashnic/hr-analytics-job-change-of-data-scientists
    """
    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/aug_test.csv?raw=true")
    df.maintain_metadata()
    assert df.data_type == {
        "enrollee_id": "id",
        "city": "nominal",
        "city_development_index": "quantitative",
        "gender": "nominal",
        "relevent_experience": "nominal",
        "enrolled_university": "nominal",
        "education_level": "nominal",
        "major_discipline": "nominal",
        "experience": "nominal",
        "company_size": "nominal",
        "company_type": "nominal",
        "last_new_job": "nominal",
        "training_hours": "quantitative",
    }


def test_id_music_data():
    """Tests in a different dataset if a column not named as an ID is recognized as an identification.
    Reference: https://www.kaggle.com/yamaerenay/spotify-dataset-19212020-160k-tracks
    """
    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/spotify.csv?raw=true")
    df["unique_num"] = df["id"]
    df.drop(columns=["id"])
    df.maintain_metadata()
    assert df.data_type == {
        "valence": "quantitative",
        "year": "temporal",
        "acousticness": "quantitative",
        "artists": "nominal",
        "danceability": "quantitative",
        "duration_ms": "quantitative",
        "energy": "quantitative",
        "explicit": "nominal",
        "unique_num": "id",
        "instrumentalness": "quantitative",
        "key": "nominal",
        "liveness": "quantitative",
        "loudness": "quantitative",
        "mode": "nominal",
        "name": "nominal",
        "popularity": "quantitative",
        "release_date": "temporal",
        "speechiness": "quantitative",
        "tempo": "quantitative",
        "id": "id",
    }


def test_id_absenteeism_data():
    """ Tests whether an id named column is not recognized because even though it is named an id, it is not with its nature. """
    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/absenteeism.csv?raw=true")
    df.maintain_metadata()
    assert df.data_type == {
        "ID": "quantitative",
        "Reason for absence": "quantitative",
        "Month of absence": "nominal",
        "Day of the week": "nominal",
        "Seasons": "nominal",
        "Transportation expense": "quantitative",
        "Distance from Residence to Work": "quantitative",
        "Service time": "nominal",
        "Age": "quantitative",
        "Work load Average/day ": "quantitative",
        "Hit target": "nominal",
        "Disciplinary failure": "nominal",
        "Education": "nominal",
        "Son": "nominal",
        "Social drinker": "nominal",
        "Social smoker": "nominal",
        "Pet": "nominal",
        "Weight": "quantitative",
        "Height": "nominal",
        "Body mass index": "nominal",
        "Absenteeism time in hours": "nominal",
    }
