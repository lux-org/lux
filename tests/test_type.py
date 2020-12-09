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


# Suite of test that checks if data_type inferred correctly by Lux
def test_check_cars():
    df = pd.read_csv("lux/data/car.csv")
    df.maintain_metadata()
    assert df.data_type_lookup["Name"] == "nominal"
    assert df.data_type_lookup["MilesPerGal"] == "quantitative"
    assert df.data_type_lookup["Cylinders"] == "nominal"
    assert df.data_type_lookup["Displacement"] == "quantitative"
    assert df.data_type_lookup["Horsepower"] == "quantitative"
    assert df.data_type_lookup["Weight"] == "quantitative"
    assert df.data_type_lookup["Acceleration"] == "quantitative"
    assert df.data_type_lookup["Year"] == "temporal"
    assert df.data_type_lookup["Origin"] == "nominal"


def test_check_int_id():
    df = pd.read_csv(
        "https://github.com/lux-org/lux-datasets/blob/master/data/instacart_sample.csv?raw=true"
    )
    df._repr_html_()
    assert len(df.data_type["id"]) == 3
    assert (
        "<code>order_id</code>, <code>product_id</code>, <code>user_id</code> is not visualized since it resembles an ID field."
        in df._message.to_html()
    )


def test_check_str_id():
    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/churn.csv?raw=true")
    df._repr_html_()
    assert (
        "<code>customerID</code> is not visualized since it resembles an ID field.</li>"
        in df._message.to_html()
    )


def test_check_hpi():
    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/hpi.csv?raw=true")
    df.maintain_metadata()

    assert df.data_type_lookup == {
        "HPIRank": "quantitative",
        "Country": "nominal",
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
    assert df.data_type_lookup == {
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
    assert df.data_type_lookup == {
        "a": "temporal",
        "b": "temporal",
        "c": "temporal",
        "d": "temporal",
        "e": "temporal",
        "f": "temporal",
        "g": "temporal",
        "h": "temporal",
    }


def test_check_stock():
    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/stocks.csv?raw=true")
    df.maintain_metadata()
    assert df.data_type_lookup == {
        "symbol": "nominal",
        "monthdate": "temporal",
        "price": "quantitative",
    }, "Stock dataset type detection error"


def test_check_college():
    df = pd.read_csv("lux/data/college.csv")
    df.maintain_metadata()
    assert df.data_type_lookup == {
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
