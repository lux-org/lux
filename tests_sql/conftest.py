import pytest
import pandas as pd
import psycopg2
import lux


@pytest.fixture(scope="session")
def global_var():
    connection = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
    lux.config.set_SQL_connection(connection)

    url = "https://github.com/lux-org/lux-datasets/blob/master/data/olympic.csv?raw=true"
    pytest.olympic = pd.read_csv(url)
    pytest.car_df = pd.read_csv("lux/data/car.csv")
    pytest.college_df = pd.read_csv("lux/data/college.csv")
    pytest.metadata = [
        "_intent",
        "_inferred_intent",
        "_data_type",
        "unique_values",
        "cardinality",
        "_rec_info",
        "_min_max",
        "plotting_style",
        "_current_vis",
        "_widget",
        "_recommendation",
        "_prev",
        "_history",
        "_saved_export",
        "name",
        "_sampled",
        "_toggle_pandas_display",
        "_message",
        "_pandas_only",
        "pre_aggregated",
        "_type_override",
    ]
