import lux
from lux.interestingness.interestingness import interestingness
from lux.compiler.Compiler import Compiler
from lux.luxDataFrame.LuxDataframe import LuxDataFrame
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
		LuxDataFrame with underspecified context.

	ignore_transpose: bool
		Boolean flag to ignore pairs of attributes whose transpose are already computed (i.e., {X,Y} will be ignored if {Y,X} is already computed)

	Returns
	-------
	recommendations : Dict[str,obj]
		object with a collection of visualizations that result from the Correlation action.
	'''

	import numpy as np
	# for benchmarking
	if ldf.toggle_benchmarking == True:
		tic = time.perf_counter()
	filter_specs = utils.get_filter_specs(ldf.context)
	query = [lux.Clause("?", data_model="measure"), lux.Clause("?", data_model="measure")]
	query.extend(filter_specs)
	vc = VisList(query,ldf)
	recommendation = {"action": "Correlation",
					  "description": "Show relationships between two quantitative attributes."}
	# Then use the data populated in the vis list to compute score
	for view in vc:
		measures = view.get_attr_by_data_model("measure")
		if len(measures) < 2: raise ValueError(
			f"Can not compute correlation between {[x.attribute for x in ldf.columns]} since less than 2 measure values present.")
		msr1 = measures[0].attribute
		msr2 = measures[1].attribute

		if (ignore_transpose):
			check_transpose = check_transpose_not_computed(vc, msr1, msr2)
		else:
			check_transpose = True
		if (check_transpose):
			view.score = interestingness(view, ldf)
		else:
			view.score = -1
	vc = vc.topK(15)
	recommendation["collection"] = vc

	# for benchmarking
	if ldf.toggle_benchmarking == True:
		toc = time.perf_counter()
		print(f"Performed correlation action in {toc - tic:0.4f} seconds")
	return recommendation


def check_transpose_not_computed(vc: VisList, a: str, b: str):
	transpose_exist = list(filter(lambda x: (x._inferred_query[0].attribute == b) and (x._inferred_query[1].attribute == a), vc))
	if (len(transpose_exist) > 0):
		return transpose_exist[0].score == -1
	else:
		return False
