import lux
from lux.interestingness.interestingness import interestingness
from lux.compiler.Compiler import Compiler
from lux.luxDataFrame.LuxDataframe import LuxDataFrame
from lux.view.ViewCollection import ViewCollection
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

	query = [lux.Spec("?",dataModel="measure"),lux.Spec("?",dataModel="measure")]
	query.extend(ldf.filterSpecs)
	vc = ViewCollection(query)
	recommendation = {"action":"Correlation",
						   "description":"Show relationships between two quantitative variables."}
	vc = vc.load(ldf)
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
	vc = vc.topK(15)
	recommendation["collection"] = vc

	#for benchmarking
	if ldf.toggleBenchmarking == True:
		toc = time.perf_counter()
		print(f"Performed correlation action in {toc - tic:0.4f} seconds")
	return recommendation

def checkTransposeNotComputed(ldf,a,b):
	# how to know if these are just columns?
	transposeExist = list(filter(lambda x:(x.specLst[0].attribute==b) and (x.specLst[1].attribute==a),ldf.viewCollection)) # Jaywoo
	if (len(transposeExist)>0):
		return transposeExist[0].score==-1
	else:
		return False