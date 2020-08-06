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
			assert vis.get_attr_by_attr_name("Geography") == []
			assert vis.get_attr_by_attr_name("PredominantDegree") != []
			assert vis.get_attr_by_attr_name("ACTMedian") != []
			assert vis.get_attr_by_attr_name("AverageFacultySalary") != []
			assert vis.get_attr_by_attr_name("SATAverage") != []
			assert vis.get_attr_by_attr_name("Expenditure") != []
			assert vis.get_attr_by_attr_name("Region") != []
			assert vis.get_attr_by_attr_name("FundingModel") != []
			assert vis.get_attr_by_attr_name("HighestDegree") != []
			assert vis.get_attr_by_attr_name("AverageCost") != []
			assert vis.get_attr_by_attr_name("AverageAgeofEntry") != []
			assert vis.get_attr_by_attr_name("AdmissionRate") != []
			assert vis.get_attr_by_attr_name("Name") != []








