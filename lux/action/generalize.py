import lux
import scipy.stats
import numpy as np
from lux.vis.Vis import Vis
from lux.compiler.Compiler import Compiler
from lux.utils import utils
from lux.interestingness.interestingness import interestingness

#for benchmarking
import time
# from compiler.Compiler import Compiler
def generalize(ldf):
	'''
	Generates all possible visualizations when one attribute or filter from the current vis is removed.

	Parameters
	----------
	ldf : lux.luxDataFrame.LuxDataFrame
		LuxDataFrame with underspecified intent.

	Returns
	-------
	recommendations : Dict[str,obj]
		object with a collection of visualizations that result from the Generalize action.
	'''
	# takes in a dataObject and generates a list of new dataObjects, each with a single measure from the original object removed
	# -->  return list of dataObjects with corresponding interestingness scores

	output = []
	excluded_columns = []
	attributes = list(filter(lambda x: x.value=="" and x.attribute!="Record", ldf._intent))
	filters = utils.get_filter_specs(ldf._intent)

	fltr_str = [fltr.attribute+fltr.filter_op+str(fltr.value) for fltr in filters]
	attr_str = [clause.attribute for clause in attributes]
	intended_attrs = '<p class="highlight-intent">'+', '.join(attr_str+fltr_str)+'</p>'

	recommendation = {"action":"Generalize",
						   "description":f"Remove an attribute or filter from {intended_attrs}."}
						    # to observe a more general trend
	# if we do no have enough column attributes or too many, return no views.
	if(len(attributes)<1 or len(attributes)>4):
		recommendation["collection"] = []
		return recommendation
	#for each column specification, create a copy of the ldf's view and remove the column specification
	#then append the view to the output
	if (len(attributes)>1):
		for clause in attributes:
			columns = clause.attribute
			if type(columns) == list:
				for column in columns:
					if column not in excluded_columns:
						temp_view = Vis(ldf.copy_intent(),score=1)
						temp_view.remove_column_from_spec(column, remove_first = True)
						excluded_columns.append(column)
						output.append(temp_view)
			elif type(columns) == str:
				if columns not in excluded_columns:
					temp_view = Vis(ldf.copy_intent(),score=1)
					temp_view.remove_column_from_spec(columns, remove_first = True)
					excluded_columns.append(columns)
			output.append(temp_view)
	#for each filter specification, create a copy of the ldf's current vis and remove the filter specification,
	#then append the view to the output
	for clause in filters:
		#new_spec = ldf._intent.copy()
		#new_spec.remove_column_from_spec(new_spec.attribute)
		temp_view = Vis(ldf.current_vis[0]._inferred_intent.copy(),source = ldf,title="Overall",score=0)
		temp_view.remove_filter_from_spec(clause.value)
		output.append(temp_view)
	
	vc = lux.vis.VisList.VisList(output,source=ldf)
	# Ignore interestingness sorting since Generalize yields very few vis (preserve order of remove attribute, then remove filters)
	# for view in vc:
	# 	view.score = interestingness(view,ldf)

	vc.remove_duplicates()
	vc.sort(remove_invalid=True)
	recommendation["collection"] = vc
	return recommendation