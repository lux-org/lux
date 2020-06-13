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
	#for benchmarking executor
	if ldf.toggleBenchmarking == True:
		ticExec = time.perf_counter()
	ldf.executor.execute(vc,ldf)
	if ldf.toggleBenchmarking == True:
		import pandas as pd
		tocExec = time.perf_counter()
		benchmarkData = {'action': ['distribution'], 'executor_type': [ldf.executorType], 'action_phase': ['viewcollection_execution'], 'time': [tocExec-ticExec]}
		benchmarkData = pd.DataFrame(data = benchmarkData)
		benchmarkData.to_csv('C:\\Users\\thyne\\Documents\\GitHub\\thyne-lux\\lux\\data\\action_benchmarking.csv', mode = 'a', header = False)
	recommendation["collection"] = vc

	#for benchmarking interestingness
	if ldf.toggleBenchmarking == True:
		ticInt = time.perf_counter()
	for view in vc:
		view.score = interestingness(view,ldf)
	if ldf.toggleBenchmarking == True:
		tocInt = time.perf_counter()
		benchmarkData = {'action': ['distribution'], 'executor_type': [ldf.executorType], 'action_phase': ['interestingness_scoring'], 'time': [tocInt-ticInt]}
		benchmarkData = pd.DataFrame(data = benchmarkData)
		benchmarkData.to_csv('C:\\Users\\thyne\\Documents\\GitHub\\thyne-lux\\lux\\data\\action_benchmarking.csv', mode = 'a', header = False)

	vc.sort()
	ldf.clearContext()
	recommendation["collection"] = vc
	# dobj.recommendations.append(recommendation)

	#for benchmarking
	if ldf.toggleBenchmarking == True:
		toc = time.perf_counter()
		benchmarkData = {'action': ['distribution'], 'executor_type': [ldf.executorType], 'action_phase':['entire_action'],'time': [toc-tic]}
		benchmarkData = pd.DataFrame(data = benchmarkData)
		benchmarkData.to_csv('C:\\Users\\thyne\\Documents\\GitHub\\thyne-lux\\lux\\data\\action_benchmarking.csv', mode = 'a', header = False)
	return recommendation