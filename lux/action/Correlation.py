import lux
from lux.interestingness.interestingness import interestingness
from lux.compiler.Compiler import Compiler
from lux.luxDataFrame.LuxDataframe import LuxDataFrame
#for benchmarking
import time
# change ignoreTranspose to false for now.
def correlation(ldf:LuxDataFrame,ignoreTranspose:bool=False):
	'''
	Generates bivariate visualizations that represent all pairwise relationships in the data.

	Parameters
	----------
	ldf : LuxDataFrame
		LuxDataFrame with underspecified context.

	ignoreTranspose: bool
		Boolean flag to ignore pairs of attributes whose transpose are already computed (i.e., {X,Y} will be ignored if {Y,X} is already computed)

	Returns
	-------
	recommendations : Dict[str,obj]
		object with a collection of visualizations that result from the Correlation action.
	'''
	import numpy as np
	#for benchmarking
	if ldf.toggleBenchmarking == True:
		tic = time.perf_counter()

	context = [lux.Spec("?",dataModel="measure"),lux.Spec("?",dataModel="measure")]
	context.extend(ldf.filterSpecs)

	ldf.setContext(context)

	recommendation = {"action":"Correlation",
						   "description":"Show relationships between two quantitative variables."}
	vc = ldf.viewCollection
	# if (ignoreIdentity): vc = filter(lambda x: x.specLst[0].attribute!=x.specLst[1].attribute,ldf.viewCollection)
	vc = Compiler.compile(ldf, vc, enumerateCollection=False)

	#for benchmarking executor
	if ldf.toggleBenchmarking == True:
		ticExec = time.perf_counter()
	ldf.executor.execute(vc,ldf)
	if ldf.toggleBenchmarking == True:
		import pandas as pd
		tocExec = time.perf_counter()
		benchmarkData = {'action': ['correlation'], 'executor_type': [ldf.executorType], 'action_phase': ['viewcollection_execution'], 'time': [tocExec-ticExec]}
		benchmarkData = pd.DataFrame(data = benchmarkData)
		benchmarkData.to_csv('C:\\Users\\thyne\\Documents\\GitHub\\thyne-lux\\lux\\data\\action_benchmarking.csv', mode = 'a', header = False)
	recommendation["collection"] = vc

	#for benchmarking interestingness calculation
	if ldf.toggleBenchmarking == True:
		ticInt = time.perf_counter()
	# Then use the data populated in the view collection to compute score
	for view in vc:
		measures = view.getAttrByDataModel("measure")
		if len(measures)<2 : raise ValueError(f"Can not compute correlation between {[x.attribute for x in ldf.columns]} since less than 2 measure values present.")
		msr1 = measures[0].attribute
		msr2 = measures[1].attribute
		
		if (ignoreTranspose):
			checkTranspose = checkTransposeNotComputed(ldf,msr1,msr2)
		else:
			checkTranspose = True
		if (checkTranspose):
			view.score = interestingness(view,ldf)
		else:
			view.score = -1
	if ldf.toggleBenchmarking == True:
		tocInt = time.perf_counter()
		benchmarkData = {'action': ['correlation'], 'executor_type': [ldf.executorType], 'action_phase': ['interestingness_scoring'], 'time': [tocInt-ticInt]}
		benchmarkData = pd.DataFrame(data = benchmarkData)
		benchmarkData.to_csv('C:\\Users\\thyne\\Documents\\GitHub\\thyne-lux\\lux\\data\\action_benchmarking.csv', mode = 'a', header = False)
	vc = vc.topK(15)
	vc.sort(removeInvalid=True)
	ldf.clearContext()
	recommendation["collection"] = vc

	#for benchmarking
	if ldf.toggleBenchmarking == True:
		toc = time.perf_counter()
		benchmarkData = {'action': ['correlation'], 'executor_type': [ldf.executorType], 'action_phase':['entire_action'],'time': [toc-tic]}
		benchmarkData = pd.DataFrame(data = benchmarkData)
		benchmarkData.to_csv('C:\\Users\\thyne\\Documents\\GitHub\\thyne-lux\\lux\\data\\action_benchmarking.csv', mode = 'a', header = False)
	return recommendation

def checkTransposeNotComputed(ldf,a,b):
	# how to know if these are just columns?
	transposeExist = list(filter(lambda x:(x.specLst[0].attribute==b) and (x.specLst[1].attribute==a),ldf.viewCollection)) # Jaywoo
	if (len(transposeExist)>0):
		return transposeExist[0].score==-1
	else:
		return False