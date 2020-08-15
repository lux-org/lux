import lux
from lux.interestingness.interestingness import interestingness
from lux.compiler.Compiler import Compiler
from lux.utils import utils

from lux.vis.Vis import Vis
from lux.vis.VisList import VisList
import pandas as pd
import time
def column_group(ldf):
	recommendation = {"action":"Column Groups",
					"description":"Shows charts of possible visualizations with respect to the column-wise index."}
	collection = []
	ldf_flat = ldf
	if isinstance(ldf.columns,pd.DatetimeIndex):
		ldf_flat.columns = ldf_flat.columns.format()
	ldf_flat = ldf_flat.reset_index() #use a single shared ldf_flat so that metadata doesn't need to be computed for every vis
	if (ldf.index.nlevels==1):
		index_column_name = ldf.index.name
		if isinstance(ldf.columns,pd.DatetimeIndex):
			ldf.columns = ldf.columns.to_native_types()
		for attribute in ldf.columns:
			vis = Vis([index_column_name,lux.Clause(str(attribute),aggregation=None)],ldf_flat)
			collection.append(vis)
	vlst = VisList(collection)
	# Note that we are not computing interestingness score here because we want to preserve the arrangement of the aggregated ldf
	
	recommendation["collection"] = vlst
	return recommendation