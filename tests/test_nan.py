from .context import lux
import pytest
import pandas as pd
import numpy as np

from lux.vis.Vis import Vis
def test_nan_column():
	df = pd.read_csv("lux/data/college.csv")
	df["Geography"] = np.nan
	df._repr_html_()
	for visList in df.recommendation.keys():
		for vis in df.recommendation[visList]:
			assert vis.get_attr_by_attr_name("Geography")==[]