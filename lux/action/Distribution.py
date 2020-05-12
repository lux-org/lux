from lux.interestingness.interestingness import interestingness
import lux
from lux.executor.PandasExecutor import PandasExecutor
from lux.executor.SQLExecutor import SQLExecutor
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
	#tic = time.perf_counter()

	if (dataTypeConstraint=="quantitative"):
		ldf.setContext([lux.Spec("?",dataType="quantitative")])
		recommendation = {"action":"Distribution",
							"description":"Show univariate count distributions of different attributes in the dataset."}
	elif (dataTypeConstraint=="nominal"):
		ldf.setContext([lux.Spec("?",dataType="nominal")])
		recommendation = {"action":"Category",
						   "description":"Show bar chart distributions of different attributes in the dataset."}

	vc = ldf.viewCollection
	if ldf.executorType == "SQL":
		SQLExecutor.execute(vc,ldf)
	elif ldf.executorType == "Pandas":
		PandasExecutor.execute(vc,ldf)
	for view in vc:
		view.score = interestingness(view,ldf)

	vc.sort()
	ldf.clearContext()
	recommendation["collection"] = vc
	# dobj.recommendations.append(recommendation)

	#for benchmarking
	#toc = time.perf_counter()
	#print(f"Performed distribution action in {toc - tic:0.4f} seconds")
	return recommendation