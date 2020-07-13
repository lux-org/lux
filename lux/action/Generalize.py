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
	excluded_columns = []
	column_spec = list(filter(lambda x: x.value=="" and x.attribute!="Record", ldf.context))
	filter_specs = utils.get_filter_specs(ldf.context)
	# if we do no have enough column attributes or too many, return no views.
	if(len(column_spec)<2 or len(column_spec)>4):
		recommendation["collection"] = []
		return recommendation
	#for each column specification, create a copy of the ldf's view and remove the column specification
	#then append the view to the output
	for spec in column_spec:
		columns = spec.attribute
		if type(columns) == list:
			for column in columns:
				if column not in excluded_columns:
					temp_view = View(ldf.context.copy(),score=1)
					temp_view.remove_column_from_spec(column, remove_first = False)
					excluded_columns.append(column)
					output.append(temp_view)
		elif type(columns) == str:
			if columns not in excluded_columns:
				temp_view = View(ldf.context.copy(),score=1)
				temp_view.remove_column_from_spec(columns, remove_first = False)
				excluded_columns.append(columns)
		output.append(temp_view)
	#for each filter specification, create a copy of the ldf's current view and remove the filter specification,
	#then append the view to the output
	for spec in filter_specs:
		#new_spec = ldf.context.copy()
		#new_spec.remove_column_from_spec(new_spec.attribute)
		temp_view = View(ldf.current_view[0].spec_lst.copy(),title="Overall",score=0)
		temp_view.remove_filter_from_spec(spec.value)
		output.append(temp_view)

	vc = lux.view.ViewCollection.ViewCollection(output)
	vc = vc.load(ldf)
	# Ignore interestingness sorting since Generalize yields very few vis (preserve order of remove attribute, then remove filters)
	# for view in vc:
	# 	view.score = interestingness(view,ldf)
	vc.remove_duplicates()
	vc.sort(remove_invalid=True)
	recommendation["collection"] = vc
	#for benchmarking
	if ldf.toggle_benchmarking == True:
		toc = time.perf_counter()
		print(f"Performed generalize action in {toc - tic:0.4f} seconds")
	return recommendation