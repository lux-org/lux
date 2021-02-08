import pandas as pd
import numpy as np
from vega_datasets import data
import altair as alt

# def sample_solution():
#     ### reccomend box plot
#     numeric_cols = list(cars.dtypes[(cars.dtypes == "float64") | (cars.dtypes == "int64")].index)

#     _facets = []

#     for c in numeric_cols:
#         _facets.append(alt.Chart(cars).mark_boxplot().encode(y=f"{c}:Q"))

#     alt.hconcat(*_facets)


'''
method: describe()

expected vis: box plot

'''

df = data.cars()
df.describe() 


