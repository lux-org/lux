import lux
from lux.interestingness.interestingness import interestingness
from lux.compiler.Compiler import Compiler
from lux.utils import utils

from lux.vis.Vis import Vis
from lux.vis.VisList import VisList
import pandas as pd
import time
def row_group(ldf):
	recommendation = {"action":"Row Groups",
					"description":"Shows charts of possible visualizations with respect to the row-wise index."}
	collection = []
	
	if (ldf.index.nlevels==1):
		if (ldf.columns.name is not None): 
			dim_name = ldf.columns.name
		else:
			dim_name = "index"
		for row_id in range(len(ldf)):
			row = ldf.iloc[row_id,]
			rowdf = row.reset_index()
			# if (dim_name =="index"): #TODO: need to change this to auto-detect
			# 	rowdf.data_type_lookup["index"]="nominal"
			# 	rowdf.data_model_lookup["index"]="dimension"
			# 	rowdf.cardinality["index"]=len(rowdf)
			# if isinstance(ldf.columns,pd.DatetimeIndex):
			# 	rowdf.data_type_lookup[dim_name]="temporal"
			vis = Vis([dim_name,lux.Clause(row.name,aggregation=None)],rowdf)
			collection.append(vis)
	vlst = VisList(collection)
	# Note that we are not computing interestingness score here because we want to preserve the arrangement of the aggregated data
	
	recommendation["collection"] = vlst
	return recommendation