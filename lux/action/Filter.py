import lux
from lux.interestingness.interestingness import interestingness
from lux.view.View import View
from lux.view.ViewCollection import ViewCollection
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
		LuxDataFrame with underspecified context.

	Returns
	-------
	recommendations : Dict[str,obj]
		object with a collection of visualizations that result from the Filter action.
	'''
	recommendation = {"action":"Filter",
						   "description":"Shows possible visualizations when filtered by categorical variables in the dataset."}
	filters = utils.get_filter_specs(ldf.context)
	filter_values = []
	output = []
	#if Row is specified, create visualizations where data is filtered by all values of the Row's categorical variable
	column_spec = utils.get_attrs_specs(ldf.current_view[0].spec_lst)
	column_spec_attr = map(lambda x: x.attribute,column_spec)
	if len(filters) > 0:
		#get unique values for all categorical values specified and creates corresponding filters
		for row in filters:
			unique_values = ldf.unique_values[row.attribute]
			filter_values.append(row.value)
			#creates views with new filters
			for val in unique_values:
				if val not in filter_values:
					new_spec = column_spec.copy()
					new_filter = lux.Spec(attribute = row.attribute, value = val)
					new_spec.append(new_filter)
					temp_view = View(new_spec)
					output.append(temp_view)
	else:	#if no existing filters, create filters using unique values from all categorical variables in the dataset
		categorical_vars = []
		for col in list(ldf.columns):
			# if cardinality is not too high, and attribute is not one of the X,Y (specified) column
			if ldf.cardinality[col]<40 and col not in column_spec_attr:
				categorical_vars.append(col)
		for cat in categorical_vars:
			unique_values = ldf.unique_values[cat]
			for i in range(0, len(unique_values)):
				new_spec = column_spec.copy()
				new_filter = lux.Spec(attribute=cat, filter_op="=",value=unique_values[i])
				new_spec.append(new_filter)
				temp_view = View(new_spec)
				output.append(temp_view)
	vc = lux.view.ViewCollection.ViewCollection(output)
	vc = vc.load(ldf)
	for view in vc:
		view.score = interestingness(view,ldf)
	vc = vc.topK(15)
	recommendation["collection"] = vc
	
	#for benchmarking
	if ldf.toggle_benchmarking == True:
		toc = time.perf_counter()
		print(f"Performed filter action in {toc - tic:0.4f} seconds")
	return recommendation