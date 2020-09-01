from .context import lux
import pytest
import pandas as pd

# Suite of test that checks if data_type inferred correctly by Lux
def test_check_cars():
    url = 'https://github.com/lux-org/lux-datasets/blob/master/data/cars.csv?raw=true'
    df = pd.read_csv(url)
    df["Year"] = pd.to_datetime(df["Year"], format='%Y') 
    df.maintain_metadata()
    assert df.data_type_lookup["Name"] == "nominal"
    assert df.data_type_lookup['MilesPerGal'] == 'quantitative'
    assert df.data_type_lookup['Cylinders'] == 'nominal'
    assert df.data_type_lookup['Displacement'] == 'quantitative'
    assert df.data_type_lookup['Horsepower'] == 'quantitative'
    assert df.data_type_lookup['Weight'] == 'quantitative'
    assert df.data_type_lookup['Acceleration'] == 'quantitative'
    assert df.data_type_lookup['Year'] == 'temporal'
    assert df.data_type_lookup['Origin'] == 'nominal'