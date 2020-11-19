import pytest
import pandas as pd


@pytest.fixture(scope="session")
def global_var():
    url = "https://github.com/lux-org/lux-datasets/blob/master/data/olympic.csv?raw=true"
    pytest.olympic = pd.read_csv(url)
    pytest.car_df = pd.read_csv("lux/data/car.csv")
    pytest.college_df = pd.read_csv("lux/data/college.csv")
