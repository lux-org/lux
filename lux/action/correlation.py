import lux
from lux.interestingness.interestingness import interestingness
from lux.processor.Compiler import Compiler
from lux.core.frame import LuxDataFrame
from lux.vis.VisList import VisList
# for benchmarking
import time
from lux.utils import utils


# change ignore_transpose to false for now.
def correlation(ldf: LuxDataFrame, ignore_transpose: bool = True):
	'''
	Generates bivariate visualizations that represent all pairwise relationships in the data.
	Parameters
	----------
	ldf : LuxDataFrame
		LuxDataFrame with underspecified intent.
	ignore_transpose: bool
		Boolean flag to ignore pairs of attributes whose transpose are already computed (i.e., {X,Y} will be ignored if {Y,X} is already computed)
	Returns
	-------
	recommendations : Dict[str,obj]
		object with a collection of visualizations that result from the Correlation action.
	'''

	import numpy as np
	filter_specs = utils.get_filter_specs(ldf._intent)
	intent = [lux.Clause("?", data_model="measure"), lux.Clause("?", data_model="measure")]
	intent.extend(filter_specs)
	vlist = VisList(intent,ldf)
	recommendation = {"action": "Correlation",
					  "description": "Show relationships between two <p class='highlight-descriptor'>quantitative</p> attributes."}
	ignore_rec_flag = False
	if (len(ldf)<5 and ldf.executor_type == "Pandas"): # Doesn't make sense to compute correlation if less than 4 data values
		ignore_rec_flag = True
	# Then use the data populated in the vis list to compute score
	for vis in vlist:
		measures = vis.get_attr_by_data_model("measure")
		if len(measures) < 2: raise ValueError(
			f"Can not compute correlation between {[x.attribute for x in ldf.columns]} since less than 2 measure values present.")
		msr1 = measures[0].attribute
		msr2 = measures[1].attribute

		if (ignore_transpose):
			check_transpose = check_transpose_not_computed(vlist, msr1, msr2)
		else:
			check_transpose = True
		if (check_transpose):
			vis.score = interestingness(vis, ldf)
		else:
			vis.score = -1
	if (ignore_rec_flag):
		recommendation["collection"] = []
		return recommendation
	vlist = vlist.topK(15)
	recommendation["collection"] = vlist
	return recommendation


def check_transpose_not_computed(vlist: VisList, a: str, b: str):
	transpose_exist = list(filter(lambda x: (x._inferred_intent[0].attribute == b) and (x._inferred_intent[1].attribute == a), vlist))
	if (len(transpose_exist) > 0):
		return transpose_exist[0].score == -1
	else:
		return False