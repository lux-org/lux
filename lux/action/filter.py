#  Copyright 2019-2020 The Lux Authors.
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import lux
from lux.interestingness.interestingness import interestingness
from lux.vis.Vis import Vis
from lux.vis.VisList import VisList
from lux.processor.Compiler import Compiler
from lux.utils import utils

def filter(ldf):
	'''
	Iterates over all possible values of a categorical variable and generates visualizations where each categorical value filters the data.

	Parameters
	----------
	ldf : lux.core.frame
		LuxDataFrame with underspecified intent.

	Returns
	-------
	recommendations : Dict[str,obj]
		object with a collection of visualizations that result from the Filter action.
	'''
	filters = utils.get_filter_specs(ldf._intent)
	filter_values = []
	output = []
	#if fltr is specified, create visualizations where data is filtered by all values of the fltr's categorical variable
	column_spec = utils.get_attrs_specs(ldf.current_vis[0]._inferred_intent)
	column_spec_attr = map(lambda x: x.attribute,column_spec)
	if len(filters) == 1:
		#get unique values for all categorical values specified and creates corresponding filters
		fltr = filters[0]
		
		if (ldf.data_type_lookup[fltr.attribute]=="ordinal" or ldf.data_type_lookup[fltr.attribute]=="nominal"):
			recommendation = {"action":"Filter",
							"description":f"Changing the <p class='highlight-intent'>{fltr.attribute}</p> filter to an alternative value."}
			unique_values = ldf.unique_values[fltr.attribute]
			filter_values.append(fltr.value)
			#creates vis with new filters
			for val in unique_values:
				if val not in filter_values:
					new_spec = column_spec.copy()
					new_filter = lux.Clause(attribute = fltr.attribute, value = val)
					new_spec.append(new_filter)
					temp_vis = Vis(new_spec)
					output.append(temp_vis)
		elif (ldf.data_type_lookup[fltr.attribute]=="quantitative"):
			recommendation = {"action":"Filter",
							"description":f"Changing the <p class='highlight-intent'>{fltr.attribute}</p> filter to an alternative inequality operation."}
			def get_complementary_ops(fltr_op):
				if (fltr_op=='>'):
					return '<='
				elif (fltr_op=='<'):
					return '>='
				elif (fltr_op=='>='):
					return '<'
				elif (fltr_op=='<='):
					return '>'
				# TODO: need to support case where fltr_op is "=" --> auto-binned ranges
			# Create vis with complementary filter operations	
			new_spec = column_spec.copy()
			new_filter = lux.Clause(attribute = fltr.attribute, filter_op=get_complementary_ops(fltr.filter_op),value = fltr.value)
			new_spec.append(new_filter)
			temp_vis = Vis(new_spec,score=1)
			output.append(temp_vis)

	else:	#if no existing filters, create filters using unique values from all categorical variables in the dataset
		intended_attrs = ', '.join([clause.attribute for clause in ldf._intent if clause.value=='' and clause.attribute!="Record"])
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
				temp_vis = Vis(new_spec)
				output.append(temp_vis)
	vlist = lux.vis.VisList.VisList(output,ldf)
	for vis in vlist:
		vis.score = interestingness(vis,ldf)
	vlist = vlist.topK(15)
	recommendation["collection"] = vlist
	return recommendation