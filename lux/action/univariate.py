from lux.interestingness.interestingness import interestingness
from lux.vis.VisList import VisList
import lux
#for benchmarking
import time
from lux.utils import utils
def univariate(ldf, data_type_constraint="quantitative"):
	'''
	Generates bar chart distributions of different attributes in the dataframe.

	Parameters
	----------
	ldf : lux.luxDataFrame.LuxDataFrame
		LuxDataFrame with underspecified intent.

	data_type_constraint: str
		Controls the type of distribution chart that will be rendered.

	Returns
	-------
	recommendations : Dict[str,obj]
		object with a collection of visualizations that result from the Distribution action.
	'''
	import scipy.stats
	import numpy as np

	#for benchmarking
	if ldf.toggle_benchmarking == True:
		tic = time.perf_counter()
	filter_specs = utils.get_filter_specs(ldf.intent)
	ignore_rec_flag = False
	if (data_type_constraint== "quantitative"):
		intent = [lux.Clause("?",data_type="quantitative")]
		intent.extend(filter_specs)
		recommendation = {"action":"Distribution",
							"description":"Show univariate histograms of <p class='highlight-text'>quantitative</p>  attributes."}
		if (len(ldf)<5): # Doesn't make sense to generate a histogram if there is less than 5 datapoints (pre-aggregated)
			ignore_rec_flag = True
	elif (data_type_constraint == "nominal"):
		intent = [lux.Clause("?",data_type="nominal")]
		intent.extend(filter_specs)
		recommendation = {"action":"Category",
						   "description":"Show value counts of <p class='highlight-text'>categorical</p> attributes."}
	elif (data_type_constraint == "temporal"):
		intent = [lux.Clause("?",data_type="temporal")]
		intent.extend(filter_specs)
		recommendation = {"action":"Temporal",
						   "description":"Show trends of counts over <p class='highlight-text'>time-related</p> attributes."}
		if (len(ldf)<3): # Doesn't make sense to generate a line chart if there is less than 3 datapoints (pre-aggregated)
			ignore_rec_flag = True
	if (ignore_rec_flag):
		recommendation["collection"] = []
		return recommendation
	vc = VisList(intent,ldf)
	for view in vc:
		view.score = interestingness(view,ldf)
	vc = vc.topK(15)
	recommendation["collection"] = vc
	#for benchmarking
	if ldf.toggle_benchmarking == True:
		toc = time.perf_counter()
		print(f"Performed distribution action in {toc - tic:0.4f} seconds")
	return recommendation