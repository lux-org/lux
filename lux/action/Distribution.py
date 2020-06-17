from lux.interestingness.interestingness import interestingness
from lux.view.ViewCollection import ViewCollection
import lux
#for benchmarking
import time

def distribution(ldf,dataTypeConstraint="quantitative"):
	'''
	Generates bar chart distributions of different attributes in the dataset.

	Parameters
	----------
	ldf : lux.luxDataFrame.LuxDataFrame
		LuxDataFrame with underspecified context.

	dataTypeConstraint: str
		The variable that controls the type of distribution chart that will be rendered.

	Returns
	-------
	recommendations : Dict[str,obj]
		object with a collection of visualizations that result from the Distribution action.
	'''
	import scipy.stats
	import numpy as np

	#for benchmarking
	if ldf.toggleBenchmarking == True:
		tic = time.perf_counter()

	if (dataTypeConstraint=="quantitative"):
		query = [lux.Spec("?",dataType="quantitative")]
		query.extend(ldf.filterSpecs)
		recommendation = {"action":"Distribution",
							"description":"Show univariate count distributions of different attributes in the dataset."}
	elif (dataTypeConstraint=="nominal"):
		query = [lux.Spec("?",dataType="nominal")]
		query.extend(ldf.filterSpecs)
		recommendation = {"action":"Category",
						   "description":"Show bar chart distributions of different attributes in the dataset."}
	vc = ViewCollection(query)
	vc = vc.load(ldf)	
	for view in vc:
		view.score = interestingness(view,ldf)
	vc = vc.topK(15)
	recommendation["collection"] = vc
	#for benchmarking
	if ldf.toggleBenchmarking == True:
		toc = time.perf_counter()
		print(f"Performed distribution action in {toc - tic:0.4f} seconds")
	return recommendation