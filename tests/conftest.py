import pytest
import pandas as pd


@pytest.fixture
def global_var():
    pytest.olympics_df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/olympic.csv?raw=true")
    pytest.car_df = pd.read_csv("lux/data/car.csv")
    url = "https://github.com/lux-org/lux-datasets/blob/master/data/state_timeseries.csv?raw=true"
    pytest.state_timeseries_df = pd.read_csv(url)
    pytest.college_df = pd.read_csv("lux/data/college.csv")
    pytest.census_df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/census.csv?raw=true")
