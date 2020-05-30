from .context import lux
import pytest
import pandas as pd
import numpy as np
from lux.interestingness.interestingness import interestingness

# The following test cases are labelled for views with <Ndim, Nmsr, Nfilter>

#TODO: interestingness test needs to validate the characteristics of the resulting recommendation ranking, e.g. skewed histograms are ranked higher than uniform ones, etc.

# def test_interestingness_1_0_0():
#     df = pd.read_csv("lux/data/car.csv")
#     df["Year"] = pd.to_datetime(df["Year"], format='%Y')
    
#     df.setContext([lux.Spec(attribute = "Origin")])
#     df.executor.execute(df.viewCollection,df)
#     assert np.isclose(interestingness(df.viewCollection[0],df), 0.0871664618628765, atol=.01)

# def test_interestingness_1_0_1():
#     df = pd.read_csv("lux/data/car.csv")
#     df["Year"] = pd.to_datetime(df["Year"], format='%Y')
    
#     df.setContext([lux.Spec(attribute = "Origin", filterOp="=",value="USA"),lux.Spec(attribute = "Origin")])
#     assert np.isclose(interestingness(df.viewCollection[0],df), 0, atol=.01)


# def test_interestingness_0_1_0():
#     df = pd.read_csv("lux/data/car.csv")
#     df["Year"] = pd.to_datetime(df["Year"], format='%Y')

#     df.setContext([lux.Spec(attribute = "Horsepower")])
#     assert np.isclose(interestingness(df.viewCollection[0],df), 40952, atol=.01)

# def test_interestingness_0_1_1():
#     df = pd.read_csv("lux/data/car.csv")
#     df["Year"] = pd.to_datetime(df["Year"], format='%Y')
    
#     df.setContext([lux.Spec(attribute = "Origin", filterOp="=",value="?"),lux.Spec(attribute = "MilesPerGal")])
#     assert np.isclose(interestingness(df.viewCollection[0],df), 0, atol=.01)

# def test_interestingness_1_1_0():
#     df = pd.read_csv("lux/data/car.csv")
#     df["Year"] = pd.to_datetime(df["Year"], format='%Y')

#     df.setContext([lux.Spec(attribute = "Horsepower"),lux.Spec(attribute = "Year")])
#     assert np.isclose(interestingness(df.viewCollection[0],df), 1088609090262702.1, atol=.01)

# def test_interestingness_1_1_1():
#     df = pd.read_csv("lux/data/car.csv")
#     df["Year"] = pd.to_datetime(df["Year"], format='%Y')

#     df.setContext([lux.Spec(attribute = "Horsepower"), lux.Spec(attribute = "Origin", filterOp="=",value = "USA", binSize=20)])
#     assert np.isclose(interestingness(df.viewCollection[0],df), 0, atol=.01)

# def test_interestingness_0_2_0():
#     df = pd.read_csv("lux/data/car.csv")
#     df["Year"] = pd.to_datetime(df["Year"], format='%Y')

#     df.setContext([lux.Spec(attribute = "Horsepower"),lux.Spec(attribute = "Acceleration")])
#     assert np.isclose(interestingness(df.viewCollection[0],df), 0.433151292343172, atol=.01)


# def test_interestingness_0_2_1():
#     df = pd.read_csv("lux/data/car.csv")
#     df["Year"] = pd.to_datetime(df["Year"], format='%Y')

#     df.setContext([lux.Spec(attribute = "Horsepower"),lux.Spec(attribute = "Acceleration"),lux.Spec(attribute = "Acceleration", filterOp=">",value = 10)])
#     # assert np.isclose(interestingness(df.viewCollection[0],df), 0.39945113787283737, atol=.01)
#     assert np.isclose(interestingness(df.viewCollection[0], df), 3438, atol=.01)