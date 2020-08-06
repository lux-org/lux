from .context import lux
import pytest
import pandas as pd
import numpy as np

from lux.vis.Vis import Vis
def test_nan_column():
	df = pd.read_csv("lux/data/college.csv")
	df_nan = df
	df_nan["Geography"]=np.nan
	# df
	# df_nan
	# assert df.recommendation["Occurrence"].__len__() - 1 == df.recommendation["Occurrence"].__len__()
	for visList in df.recommendation.keys():
		for vis in df.recommendation[visList]:
			with pytest.raises(Exception) as e_info:
				vis.get_attr_by_attr_name("Geography")