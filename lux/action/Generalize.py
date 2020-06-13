import lux
import scipy.stats
import numpy as np
from lux.view.View import View
from lux.compiler.Compiler import Compiler
from lux.utils import utils
from lux.interestingness.interestingness import interestingness

#for benchmarking
import time
# from compiler.Compiler import Compiler
def generalize(ldf):
	#for benchmarking
	if ldf.toggleBenchmarking == True:
		tic = time.perf_counter()
	'''
	Generates all possible visualizations when one attribute or filter from the current view is removed.

	Parameters
	----------
	ldf : lux.luxDataFrame.LuxDataFrame
		LuxDataFrame with underspecified context.

	Returns
	-------
	recommendations : Dict[str,obj]
		object with a collection of visualizations that result from the Generalize action.
	'''
	# takes in a dataObject and generates a list of new dataObjects, each with a single measure from the original object removed
	# -->  return list of dataObjects with corresponding interestingness scores

	recommendation = {"action":"Generalize",
						   "description":"Remove one attribute or filter to observe a more general trend."}
	output = []
	excludedColumns = []
	columnSpec = utils.getAttrsSpecs(ldf.context)
	rowSpecs = utils.getFilterSpecs(ldf.context)
	# if we do no have enough column attributes or too many, return no views.
	if(len(columnSpec)<2 or len(columnSpec)>4):
		recommendation["collection"] = []
		return recommendation
	for spec in columnSpec:
		columns = spec.attribute
		if type(columns) == list:
			for column in columns:
				if column not in excludedColumns:
					tempView = View(ldf.context)
					tempView.removeColumnFromSpecNew(column)
					excludedColumns.append(column)
					output.append(tempView)
		elif type(columns) == str:
			if columns not in excludedColumns:
				tempView = View(ldf.context)
				tempView.removeColumnFromSpecNew(columns)
				excludedColumns.append(columns)
		output.append(tempView)
	for i, spec in enumerate(rowSpecs):
		newSpec = ldf.context.copy()
		newSpec.pop(i)
		tempView = View(newSpec)
		output.append(tempView)
		
	vc = lux.view.ViewCollection.ViewCollection(output)
	vc = Compiler.compile(ldf,vc,enumerateCollection=False)

	#for benchmarking executor
	if ldf.toggleBenchmarking == True:
		ticExec = time.perf_counter()
	ldf.executor.execute(vc,ldf)
	if ldf.toggleBenchmarking == True:
		tocExec = time.perf_counter()
		benchmarkData = {'action': ['generalize'], 'executor_type': [ldf.executorType], 'action_phase': ['viewcollection_execution'], 'time': [tocExec-ticExec]}
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
		benchmarkData = {'action': ['generalize'], 'executor_type': [ldf.executorType], 'action_phase': ['interestingness_scoring'], 'time': [tocInt-ticInt]}
		benchmarkData = pd.DataFrame(data = benchmarkData)
		benchmarkData.to_csv('C:\\Users\\thyne\\Documents\\GitHub\\thyne-lux\\lux\\data\\action_benchmarking.csv', mode = 'a', header = False)
	vc = vc.topK(10)
	vc.sort(removeInvalid=True)
	#for benchmarking
	if ldf.toggleBenchmarking == True:
		import pandas as pd
		toc = time.perf_counter()
		benchmarkData = {'action': ['generalize'], 'executor_type': [ldf.executorType], 'action_phase':['entire_action'],'time': [toc-tic]}
		benchmarkData = pd.DataFrame(data = benchmarkData)
		benchmarkData.to_csv('C:\\Users\\thyne\\Documents\\GitHub\\thyne-lux\\lux\\data\\action_benchmarking.csv', mode = 'a', header = False)
	return recommendation