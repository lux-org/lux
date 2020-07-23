from .context import lux
import pytest
import pandas as pd

from lux.vis.Vis import Vis
def test_vary_filter_val():
    df = pd.read_csv("lux/data/olympic.csv")
    vis = Vis(["Height","SportType=Ball"],df)
    df.set_context_as_vis(vis)
    df.show_more()
    assert len(df.recommendation["Filter"]) == len(df["SportType"].unique())-1

#test case for generalize action with more than 2 variables specified in context
def test_generalize_action():
	df = pd.read_csv("lux/data/car.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y') 
	df.set_context(["Cylinders", "Horsepower", "MilesPerGal"])
	df.show_more()

	assert len(df.recommendation['Generalize']) == 3

	#check that all graphs are unique
	spec_lst1 = df.recommendation['Generalize'][0].spec_lst
	spec_lst2 = df.recommendation['Generalize'][1].spec_lst
	spec_lst3 = df.recommendation['Generalize'][2].spec_lst

	assert spec_lst1 != spec_lst2 and spec_lst1 != spec_lst3 and spec_lst2 != spec_lst3
