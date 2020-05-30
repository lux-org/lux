from lux.interestingness.interestingness import interestingness
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
		context = [lux.Spec("?",dataType="quantitative")]
		context.extend(ldf.filterSpecs)
		ldf.setContext(context)
		recommendation = {"action":"Distribution",
							"description":"Show univariate count distributions of different attributes in the dataset."}
	elif (dataTypeConstraint=="nominal"):
		context = [lux.Spec("?",dataType="nominal")]
		context.extend(ldf.filterSpecs)
		ldf.setContext(context)
		recommendation = {"action":"Category",
						   "description":"Show bar chart distributions of different attributes in the dataset."}

	vc = ldf.viewCollection
	ldf.executor.execute(vc,ldf)
	for view in vc:
		view.score = interestingness(view,ldf)

	vc.sort()
	ldf.clearContext()
	recommendation["collection"] = vc
	# dobj.recommendations.append(recommendation)

	#for benchmarking
	if ldf.toggleBenchmarking == True:
		toc = time.perf_counter()
		print(f"Performed distribution action in {toc - tic:0.4f} seconds")
	return recommendation