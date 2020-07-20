from lux.vis import VisSpec
from typing import List, Dict, Union
from lux.vis.Vis import Vis
from lux.luxDataFrame.LuxDataframe import LuxDataFrame
from lux.vis.VisCollection import VisCollection
from lux.utils import date_utils
import pandas as pd
import numpy as np


class Compiler:
	'''
	Given a context with underspecified inputs, compile the context into fully specified visualizations for visualization.
	'''

	def __init__(self):
		self.name = "Compiler"

	def __repr__(self):
		return f"<Compiler>"

	@staticmethod
	def compile(ldf: LuxDataFrame,spec_lst:List[VisSpec], vis_collection: VisCollection, enumerate_collection=True) -> VisCollection:
		"""
		Compiles input specifications in the context of the ldf into a collection of lux.vis objects for visualization.
		1) Enumerate a collection of visualizations interested by the user to generate a vis collection
		2) Expand underspecified specifications(lux.VisSpec) for each of the generated visualizations.
		3) Determine encoding properties for each vis

		Parameters
		----------
		ldf : lux.luxDataFrame.LuxDataFrame
			LuxDataFrame with underspecified context.
		vis_collection : list[lux.vis.Vis]
			empty list that will be populated with specified lux.Vis objects.
		enumerate_collection : boolean
			A boolean value that signals when to generate a collection of visualizations.

		Returns
		-------
		vis_collection: list[lux.Vis]
			vis collection with compiled lux.Vis objects.
		"""
		if (enumerate_collection):
			vis_collection = Compiler.enumerate_collection(spec_lst,ldf)
		vis_collection = Compiler.expand_underspecified(ldf, vis_collection)  # autofill data type/model information
		if len(vis_collection)>1: 
			vis_collection = Compiler.remove_all_invalid(vis_collection) # remove invalid visualizations from collection
		for vis in vis_collection:
			Compiler.determine_encoding(ldf, vis)  # autofill viz related information
		return vis_collection

	@staticmethod
	def enumerate_collection(spec_lst:List[VisSpec],ldf: LuxDataFrame) -> VisCollection:
		"""
		Given specifications that have been expanded thorught populateOptions,
		recursively iterate over the resulting list combinations to generate a Vis collection.

		Parameters
		----------
		ldf : lux.luxDataFrame.LuxDataFrame
			LuxDataFrame with underspecified context.

		Returns
		-------
		VisCollection: list[lux.Vis]
			vis collection with compiled lux.Vis objects.
		"""
		import copy
		specs = Compiler.populate_wildcard_options(spec_lst, ldf)
		attributes = specs['attributes']
		filters = specs['filters']
		if len(attributes) == 0 and len(filters) > 0:
			ldf.filter_specs = filters
			return []

		collection = []

		# TODO: generate combinations of column attributes recursively by continuing to accumulate attributes for len(colAtrr) times
		def combine(col_attrs, accum):
			last = (len(col_attrs) == 1)
			n = len(col_attrs[0])
			for i in range(n):
				column_list = copy.deepcopy(accum + [col_attrs[0][i]])
				if last:
					if len(filters) > 0:  # if we have filters, generate combinations for each row.
						for row in filters:
							spec_lst = copy.deepcopy(column_list + [row])
							vis = Vis(spec_lst, title=f"{row.attribute} {row.filter_op} {row.value}")
							collection.append(vis)
					else:
						vis = Vis(column_list)
						collection.append(vis)
				else:
					combine(col_attrs[1:], column_list)
		combine(attributes, [])
		return VisCollection(collection)

	@staticmethod
	def expand_underspecified(ldf, vis_collection) -> VisCollection:
		"""
		Given a underspecified VisSpec, populate the data_type and data_model information accordingly

		Parameters
		----------
		ldf : lux.luxDataFrame.LuxDataFrame
			LuxDataFrame with underspecified context

		vis_collection : list[lux.vis.Vis]
			List of lux.Vis objects that will have their underspecified VisSpec details filled out.
		Returns
		-------
		vc: VisCollection
			vis collection with compiled lux.Vis objects.
		"""		
		# TODO: copy might not be neccesary
		import copy
		vc = copy.deepcopy(vis_collection)  # Preserve the original dobj
		for vis in vc:
			for spec in vis.spec_lst:
				if spec.description == "?":
					spec.description = ""
				if spec.attribute:
					if (spec.data_type == ""):
						spec.data_type = ldf.data_type_lookup[spec.attribute]
					if (spec.data_model == ""):
						spec.data_model = ldf.data_model_lookup[spec.attribute]
				if (spec.value!=""):
					if(isinstance(spec.value,np.datetime64)):
						# TODO: Make this more general and not specific to Year attributes
						chart_title = date_utils.date_formatter(spec.value,ldf)
					else:
						chart_title = spec.value
					vis.title = f"{spec.attribute} {spec.filter_op} {chart_title}"
		return vc

	@staticmethod
	def remove_all_invalid(vis_collection:VisCollection) -> VisCollection:
		"""
		Given an expanded vis collection, remove all visualizations that are invalid.
		Currently, the invalid visualizations are ones that contain two of the same attribute, no more than two temporal attributes, or overlapping attributes (same filter attribute and visualized attribute).
		Parameters
		----------
		vis_collection : list[lux.vis.Vis]
			empty list that will be populated with specified lux.Vis objects.
		Returns
		-------
		lux.vis.VisCollection
			vis collection with compiled lux.Vis objects.
		"""
		new_vc = []
		for vis in vis_collection:
			num_temporal_specs = 0
			attribute_set = set()
			for spec in vis.spec_lst:
				attribute_set.add(spec.attribute)
				if spec.data_type == "temporal":
					num_temporal_specs += 1
			all_distinct_specs = 0 == len(vis.spec_lst) - len(attribute_set)
			if num_temporal_specs < 2 and all_distinct_specs:
				new_vc.append(vis)

		return VisCollection(new_vc)

	@staticmethod
	def determine_encoding(ldf: LuxDataFrame, vis: Vis):
		'''
		Populates Vis with the appropriate mark type and channel information based on ShowMe logic
		Currently support up to 3 dimensions or measures
		
		Parameters
		----------
		ldf : lux.luxDataFrame.LuxDataFrame
			LuxDataFrame with underspecified context
		vis : lux.vis.Vis

		Returns
		-------
		None

		Notes
		-----
		Implementing automatic encoding from Tableau's VizQL
		Mackinlay, J. D., Hanrahan, P., & Stolte, C. (2007).
		Show Me: Automatic presentation for visual analysis.
		IEEE Transactions on Visualization and Computer Graphics, 13(6), 1137–1144.
		https://doi.org/10.1109/TVCG.2007.70594
		'''
		# Count number of measures and dimensions
		ndim = 0
		nmsr = 0
		filters = []
		for spec in vis.spec_lst:
			if (spec.value==""):
				if (spec.data_model == "dimension"):
					ndim += 1
				elif (spec.data_model == "measure" and spec.attribute!="Record"):
					nmsr += 1
			else:  # preserve to add back to spec_lst later
				filters.append(spec)
		# Helper function (TODO: Move this into utils)
		def line_or_bar(ldf, dimension:VisSpec, measure:VisSpec):
			dim_type = dimension.data_type
			# If no aggregation function is specified, then default as average
			if (measure.aggregation==""):
				measure.set_aggregation("mean")
			if (dim_type == "temporal" or dim_type == "oridinal"):
				return "line", {"x": dimension, "y": measure}
			else:  # unordered categorical
				# if cardinality large than 5 then sort bars
				if ldf.cardinality[dimension.attribute]>5:
					dimension.sort = "ascending"
				return "bar", {"x": measure, "y": dimension}
		

		# ShowMe logic + additional heuristics
		#count_col = VisSpec( attribute="count()", data_model="measure")
		count_col = VisSpec( attribute="Record", aggregation="count", data_model="measure", data_type="quantitative")
		auto_channel={}
		if (ndim == 0 and nmsr == 1):
			# Histogram with Count 
			measure = vis.get_attr_by_data_model("measure",exclude_record=True)[0]
			if (len(vis.get_attr_by_attr_name("Record"))<0):
				vis.spec_lst.append(count_col)
			# If no bin specified, then default as 10
			if (measure.bin_size == 0):
				measure.bin_size = 10
			auto_channel = {"x": measure, "y": count_col}
			vis.x_min_max = ldf.x_min_max
			vis.mark = "histogram"
		elif (ndim == 1 and (nmsr == 0 or nmsr == 1)):
			# Line or Bar Chart
			if (nmsr == 0):
				vis.spec_lst.append(count_col)
			dimension = vis.get_attr_by_data_model("dimension")[0]
			measure = vis.get_attr_by_data_model("measure")[0]
			vis.mark, auto_channel = line_or_bar(ldf, dimension, measure)
		elif (ndim == 2 and (nmsr == 0 or nmsr == 1)):
			# Line or Bar chart broken down by the dimension
			dimensions = vis.get_attr_by_data_model("dimension")
			d1 = dimensions[0]
			d2 = dimensions[1]
			if (ldf.cardinality[d1.attribute] < ldf.cardinality[d2.attribute]):
				# d1.channel = "color"
				vis.remove_column_from_spec(d1.attribute)
				dimension = d2
				color_attr = d1
			else:
				if (d1.attribute == d2.attribute):
					vis.spec_lst.pop(
						0)  # if same attribute then remove_column_from_spec will remove both dims, we only want to remove one
				else:
					vis.remove_column_from_spec(d2.attribute)
				dimension = d1
				color_attr = d2
			# Colored Bar/Line chart with Count as default measure
			if (nmsr == 0):
				vis.spec_lst.append(count_col)
			measure = vis.get_attr_by_data_model("measure")[0]
			vis.mark, auto_channel = line_or_bar(ldf, dimension, measure)
			auto_channel["color"] = color_attr
		elif (ndim == 0 and nmsr == 2):
			# Scatterplot
			vis.x_min_max = ldf.x_min_max
			vis.y_min_max = ldf.y_min_max
			vis.mark = "scatter"
			auto_channel = {"x": vis.spec_lst[0],
						   "y": vis.spec_lst[1]}
		elif (ndim == 1 and nmsr == 2):
			# Scatterplot broken down by the dimension
			measure = vis.get_attr_by_data_model("measure")
			m1 = measure[0]
			m2 = measure[1]

			color_attr = vis.get_attr_by_data_model("dimension")[0]
			vis.remove_column_from_spec(color_attr)
			vis.x_min_max = ldf.x_min_max
			vis.y_min_max = ldf.y_min_max
			vis.mark = "scatter"
			auto_channel = {"x": m1,
						   "y": m2,
						   "color": color_attr}
		elif (ndim == 0 and nmsr == 3):
			# Scatterplot with color
			vis.x_min_max = ldf.x_min_max
			vis.y_min_max = ldf.y_min_max
			vis.mark = "scatter"
			auto_channel = {"x": vis.spec_lst[0],
						   "y": vis.spec_lst[1],
						   "color": vis.spec_lst[2]}
		if (auto_channel!={}):
			vis = Compiler.enforce_specified_channel(vis, auto_channel)
			vis.spec_lst.extend(filters)  # add back the preserved filters

	@staticmethod
	def enforce_specified_channel(vis: Vis, auto_channel: Dict[str, str]):
		"""
		Enforces that the channels specified in the Vis by users overrides the showMe autoChannels.
		
		Parameters
		----------
		vis : lux.vis.Vis
			Input Vis without channel specification.
		auto_channel : Dict[str,str]
			Key-value pair in the form [channel: attributeName] specifying the showMe recommended channel location.
		
		Returns
		-------
		vis : lux.vis.Vis
			Vis with channel specification combining both original and auto_channel specification.
		
		Raises
		------
		ValueError
			Ensures no more than one attribute is placed in the same channel.
		"""
		result_dict = {}  # result of enforcing specified channel will be stored in result_dict
		specified_dict = {}  # specified_dict={"x":[],"y":[list of Dobj with y specified as channel]}
		# create a dictionary of specified channels in the given dobj
		for val in auto_channel.keys():
			specified_dict[val] = vis.get_attr_by_channel(val)
			result_dict[val] = ""
		# for every element, replace with what's in specified_dict if specified
		for sVal, sAttr in specified_dict.items():
			if (len(sAttr) == 1):  # if specified in dobj
				# remove the specified channel from auto_channel (matching by value, since channel key may not be same)
				for i in list(auto_channel.keys()):
					if ((auto_channel[i].attribute == sAttr[0].attribute)
						and (auto_channel[i].channel == sVal)): # need to ensure that the channel is the same (edge case when duplicate Cols with same attribute name)
						auto_channel.pop(i)
						break
				sAttr[0].channel = sVal
				result_dict[sVal] = sAttr[0]
			elif (len(sAttr) > 1):
				raise ValueError("There should not be more than one attribute specified in the same channel.")
		# For the leftover channels that are still unspecified in result_dict,
		# and the leftovers in the auto_channel specification,
		# step through them together and fill it automatically.
		leftover_channels = list(filter(lambda x: result_dict[x] == '', result_dict))
		for leftover_channel, leftover_encoding in zip(leftover_channels, auto_channel.values()):
			leftover_encoding.channel = leftover_channel
			result_dict[leftover_channel] = leftover_encoding
		vis.spec_lst = list(result_dict.values())
		return vis

	@staticmethod
	# def populate_wildcard_options(ldf: LuxDataFrame) -> dict:
	def populate_wildcard_options(spec_lst:List[VisSpec], ldf: LuxDataFrame) -> dict:
		"""
		Given wildcards and constraints in the LuxDataFrame's context,
		return the list of available values that satisfies the data_type or data_model constraints.

		Parameters
		----------
		ldf : LuxDataFrame
			LuxDataFrame with row or attributes populated with available wildcard options.

		Returns
		-------
		specs: Dict[str,list]
			a dictionary that holds the attributes and filters generated from wildcards and constraints.
		"""
		import copy
		from lux.utils.utils import convert_to_list

		specs = {"attributes": [], "filters": []}
		for spec in spec_lst:
			spec_options = []
			if spec.value == "":  # attribute
				if spec.attribute == "?":
					options = set(list(ldf.columns))  # all attributes
					if (spec.data_type != ""):
						options = options.intersection(set(ldf.data_type[spec.data_type]))
					if (spec.data_model != ""):
						options = options.intersection(set(ldf.data_model[spec.data_model]))
					options = list(options)
				else:
					options = convert_to_list(spec.attribute)
				for optStr in options:
					if str(optStr) not in spec.exclude:
						spec_copy = copy.copy(spec)
						spec_copy.attribute = optStr
						spec_options.append(spec_copy)
				specs["attributes"].append(spec_options)
			else:  # filters
				attr_lst = convert_to_list(spec.attribute)
				for attr in attr_lst:
					options = []
					if spec.value == "?":
						options = ldf.unique_values[attr]
						specInd = spec_lst.index(spec)
						spec_lst[specInd] = VisSpec(attribute=spec.attribute, filter_op="=", value=list(options))
					else:
						options.extend(convert_to_list(spec.value))
					for optStr in options:
						if str(optStr) not in spec.exclude:
							spec_copy = copy.copy(spec)
							spec_copy.attribute = attr
							spec_copy.value = optStr
							spec_options.append(spec_copy)
				specs["filters"].extend(spec_options)

		return specs
