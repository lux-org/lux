from .context import lux
import pytest
import pandas as pd
import numpy as np

from lux.vis.Vis import Vis
def test_nan_column():
	df = pd.read_csv("lux/data/college.csv")
	df_nan = df
	df_nan["Geography"]=np.nan
	for visList in df.recommendation.keys():
		for vis in df.recommendation[visList]:
			for col in list(filter(lambda x: x!="Geography",df.columns)): assert vis.get_attr_by_attr_name(col)!=[]








