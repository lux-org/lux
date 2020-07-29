import lux
from lux.interestingness.interestingness import interestingness
from lux.vis.Vis import Vis
from lux.vis.VisList import VisList
from lux.compiler.Compiler import Compiler
from lux.utils import utils

#for benchmarking
import time

def filter(ldf):
	#for benchmarking
	if ldf.toggle_benchmarking == True:
		tic = time.perf_counter()
	'''
	Iterates over all possible values of a categorical variable and generates visualizations where each categorical value filters the data.

	Parameters
	----------
	ldf : lux.luxDataFrame.LuxDataFrame
		LuxDataFrame with underspecified intent.

	Returns
	-------
	recommendations : Dict[str,obj]
		object with a collection of visualizations that result from the Filter action.
	'''
	
	filters = utils.get_filter_specs(ldf.intent)
	filter_values = []
	output = []
	#if fltr is specified, create visualizations where data is filtered by all values of the fltr's categorical variable
	column_spec = utils.get_attrs_specs(ldf.current_vis[0]._inferred_intent)
	column_spec_attr = map(lambda x: x.attribute,column_spec)
	if len(filters) == 1:
		#get unique values for all categorical values specified and creates corresponding filters
		fltr = filters[0]
		unique_values = ldf.unique_values[fltr.attribute]
		filter_values.append(fltr.value)
		#creates views with new filters
		for val in unique_values:
			if val not in filter_values:
				new_spec = column_spec.copy()
				new_filter = lux.Clause(attribute = fltr.attribute, value = val)
				new_spec.append(new_filter)
				temp_view = Vis(new_spec)
				output.append(temp_view)
		recommendation = {"action":"Filter",
					 	  "description":f"Changing the <p class='highlight-intent'>{fltr.attribute}</p> filter to an alternative value."}
	else:	#if no existing filters, create filters using unique values from all categorical variables in the dataset
		intended_attrs = '<b>'+', '.join([clause.attribute for clause in ldf.intent if clause.value=='' and clause.attribute!="Record"])+'</b>'
		recommendation = {"action":"Filter",
					 "description":f"Applying filters to the <p class='highlight-intent'>{intended_attrs}</p> intent."}
		categorical_vars = []
		for col in list(ldf.columns):
			# if cardinality is not too high, and attribute is not one of the X,Y (specified) column
			if ldf.cardinality[col]<30 and col not in column_spec_attr:
				categorical_vars.append(col)
		for cat in categorical_vars:
			unique_values = ldf.unique_values[cat]
			for i in range(0, len(unique_values)):
				new_spec = column_spec.copy()
				new_filter = lux.Clause(attribute=cat, filter_op="=",value=unique_values[i])
				new_spec.append(new_filter)
				temp_view = Vis(new_spec)
				output.append(temp_view)
	vc = lux.vis.VisList.VisList(output,ldf)
	for view in vc:
		view.score = interestingness(view,ldf)
	vc = vc.topK(15)
	recommendation["collection"] = vc
	
	#for benchmarking
	if ldf.toggle_benchmarking == True:
		toc = time.perf_counter()
		print(f"Performed filter action in {toc - tic:0.4f} seconds")
	return recommendation