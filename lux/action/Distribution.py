from lux.interestingness.interestingness import interestingness
from lux.view.ViewCollection import ViewCollection
import lux
#for benchmarking
import time

def distribution(ldf, data_type_constraint="quantitative"):
	'''
	Generates bar chart distributions of different attributes in the dataset.

	Parameters
	----------
	ldf : lux.luxDataFrame.LuxDataFrame
		LuxDataFrame with underspecified context.

	data_type_constraint: str
		The variable that controls the type of distribution chart that will be rendered.

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

	if (data_type_constraint== "quantitative"):
		query = [lux.Spec("?",data_type="quantitative")]
		query.extend(ldf.filter_specs)
		recommendation = {"action":"Distribution",
							"description":"Show univariate count distributions of different attributes in the dataset."}
	elif (data_type_constraint == "nominal"):
		query = [lux.Spec("?",data_type="nominal")]
		query.extend(ldf.filter_specs)
		recommendation = {"action":"Category",
						   "description":"Show bar chart distributions of different attributes in the dataset."}
	vc = ViewCollection(query)
	vc = vc.load(ldf)	
	for view in vc:
		view.score = interestingness(view,ldf)
	vc = vc.topK(15)
	recommendation["collection"] = vc
	#for benchmarking
	if ldf.toggle_benchmarking == True:
		toc = time.perf_counter()
		print(f"Performed distribution action in {toc - tic:0.4f} seconds")
	return recommendation