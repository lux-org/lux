import pandas as pd
import numpy as np
from vega_datasets import data
import altair as alt

def sample_solution():
    alt.Chart(cars).mark_bar().encode(
    x="Origin", 
    y="count()")

def test_function():
    print("I was called")


'''
method: value_counts()
expected vis: histogram

'''
test_function()

df = data.cars()
small_df = df[["Name", "Origin"]]

df.Origin.value_counts()