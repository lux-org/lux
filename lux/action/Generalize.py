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
	vc = vc.load(ldf)
	recommendation["collection"] = vc
	for view in vc:
		view.score = interestingness(view,ldf)
	vc.sort(removeInvalid=True)
	#for benchmarking
	if ldf.toggleBenchmarking == True:
		toc = time.perf_counter()
		print(f"Performed generalize action in {toc - tic:0.4f} seconds")
	return recommendation