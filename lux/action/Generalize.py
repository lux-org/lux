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
	if ldf.toggle_benchmarking == True:
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
	column_spec = list(filter(lambda x: x.value=="" and x.attribute!="Record", ldf.context))
	rowSpecs = utils.get_filter_specs(ldf.context)
	# if we do no have enough column attributes or too many, return no views.
	if(len(column_spec)<2 or len(column_spec)>4):
		recommendation["collection"] = []
		return recommendation
	for spec in column_spec:
		columns = spec.attribute
		if type(columns) == list:
			for column in columns:
				if column not in excludedColumns:
					tempView = View(ldf.context)
					tempView.remove_column_from_spec_new(column)
					excludedColumns.append(column)
					output.append(tempView)
		elif type(columns) == str:
			if columns not in excludedColumns:
				tempView = View(ldf.context)
				tempView.remove_column_from_spec_new(columns)
				excludedColumns.append(columns)
		output.append(tempView)
	for i, spec in enumerate(rowSpecs):
		new_spec = ldf.context.copy()
		new_spec.pop(i)
		tempView = View(new_spec)
		output.append(tempView)
		
	vc = lux.view.ViewCollection.ViewCollection(output)
	vc = vc.load(ldf)
	recommendation["collection"] = vc
	for view in vc:
		view.score = interestingness(view,ldf)
	vc.sort(remove_invalid=True)
	#for benchmarking
	if ldf.toggle_benchmarking == True:
		toc = time.perf_counter()
		print(f"Performed generalize action in {toc - tic:0.4f} seconds")
	return recommendation