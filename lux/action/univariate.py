from lux.interestingness.interestingness import interestingness
from lux.vis.VisList import VisList
import lux
#for benchmarking
import time
from lux.utils import utils
def univariate(ldf, *args):
	'''
	Generates bar chart distributions of different attributes in the dataframe.

	Parameters
	----------
	ldf : lux.core.frame
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

	if len(args) == 0:
		data_type_constraint = "quantitative"
	else:
		data_type_constraint = args[0][0]

	filter_specs = utils.get_filter_specs(ldf._intent)
	ignore_rec_flag = False
	if (data_type_constraint== "quantitative"):
		intent = [lux.Clause("?",data_type="quantitative",exclude="Number of Records")]
		intent.extend(filter_specs)
		recommendation = {"action":"Distribution",
						  "description":"Show univariate histograms of <p class='highlight-descriptor'>quantitative</p>  attributes."}
		if (len(ldf)<5): # Doesn't make sense to generate a histogram if there is less than 5 datapoints (pre-aggregated)
			ignore_rec_flag = True
	elif (data_type_constraint == "nominal"):
		intent = [lux.Clause("?",data_type="nominal")]
		intent.extend(filter_specs)
		recommendation = {"action":"Occurrence",
						   "description":"Show frequency of occurrence for <p class='highlight-descriptor'>categorical</p> attributes."}
	elif (data_type_constraint == "temporal"):
		intent = [lux.Clause("?",data_type="temporal")]
		intent.extend(filter_specs)
		recommendation = {"action":"Temporal",
						   "description":"Show trends over <p class='highlight-descriptor'>time-related</p> attributes."}
		if (len(ldf)<3): # Doesn't make sense to generate a line chart if there is less than 3 datapoints (pre-aggregated)
			ignore_rec_flag = True
	if (ignore_rec_flag):
		recommendation["collection"] = []
		return recommendation
	vlist = VisList(intent,ldf)
	for vis in vlist:
		vis.score = interestingness(vis,ldf)
	vlist = vlist.topK(15)
	recommendation["collection"] = vlist
	return recommendation