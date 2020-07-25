from .context import lux
import pytest
import pandas as pd

# Test suite for checking if the expected errors and warnings are showing up correctly
def test_context_str_error():
    df = pd.read_csv("lux/data/college.csv")
    with pytest.raises(TypeError,match="Input context must be a list"):
        df.set_intent("bad string input")
def test_export_b4_widget_created():
    df = pd.read_csv("lux/data/college.csv")
    with pytest.warns(UserWarning,match="No widget attached to the dataframe"):
        df.get_exported()