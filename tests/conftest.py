import pytest
import pandas as pd

@pytest.fixture(scope="session")
def global_var():
    pytest.olympics_df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/olympic.csv?raw=true")
    pytest.car_df = pd.read_csv("lux/data/car.csv")
    pytest.college_df = pd.read_csv("lux/data/college.csv")