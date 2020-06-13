from lux.context import Spec
from typing import List, Dict, Union
from lux.view.View import View
from lux.luxDataFrame.LuxDataframe import LuxDataFrame
from lux.view.ViewCollection import ViewCollection
import pandas as pd
import numpy as np


class Compiler:
	'''
	Given a context with underspecified inputs, compile the context into fully specified views for visualization.
	'''

	def __init__(self):
		self.name = "Compiler"

	def __repr__(self):
		return f"<Compiler>"

	@staticmethod
	def compile(ldf: LuxDataFrame,specLst:List[Spec], viewCollection: ViewCollection, enumerateCollection=True) -> ViewCollection:
		"""
		Compiles input specifications in the context of the ldf into a collection of lux.View objects for visualization.
		1) Enumerate a collection of views interested by the user to generate a view collection
		2) Expand underspecified specifications(lux.Spec) for each of the generated views.
		3) Determine encoding properties for each view

		Parameters
		----------
		ldf : lux.luxDataFrame.LuxDataFrame
			LuxDataFrame with underspecified context.
		viewCollection : list[lux.view.View]
			empty list that will be populated with specified lux.View objects.
		enumerateCollection : boolean
			A boolean value that signals when to generate a collection of visualizations.

		Returns
		-------
		viewCollection: list[lux.View]
			view collection with compiled lux.View objects.
		"""
		if (enumerateCollection):
			viewCollection = Compiler.enumerateCollection(specLst,ldf)
		viewCollection = Compiler.expandUnderspecified(ldf, viewCollection)  # autofill data type/model information
		if len(viewCollection)>1: 
			viewCollection = Compiler.removeAllInvalid(viewCollection) # remove invalid views from collection
		for view in viewCollection:
			Compiler.determineEncoding(ldf, view)  # autofill viz related information
		return viewCollection

	@staticmethod
	def enumerateCollection(specLst:List[Spec],ldf: LuxDataFrame) -> ViewCollection:
		"""
		Given specifications that have been expanded thorught populateOptions,
		recursively iterate over the resulting list combinations to generate a View collection.

		Parameters
		----------
		ldf : lux.luxDataFrame.LuxDataFrame
			LuxDataFrame with underspecified context.

		Returns
		-------
		ViewCollection: list[lux.View]
			view collection with compiled lux.View objects.
		"""
		import copy
		specs = Compiler.populateWildcardOptions(specLst,ldf)
		attributes = specs['attributes']
		filters = specs['filters']
		if len(attributes) == 0 and len(filters) > 0:
			ldf.filterSpecs = filters
			return []

		collection = []

		# TODO: generate combinations of column attributes recursively by continuing to accumulate attributes for len(colAtrr) times
		def combine(colAttrs, accum):
			last = (len(colAttrs) == 1)
			n = len(colAttrs[0])
			for i in range(n):
				columnList = copy.deepcopy(accum + [colAttrs[0][i]])
				if last:
					if len(filters) > 0:  # if we have filters, generate combinations for each row.
						for row in filters:
							specLst = copy.deepcopy(columnList + [row])
							view = View(specLst, title=f"{row.attribute} {row.filterOp} {row.value}")
							collection.append(view)
					else:
						view = View(columnList)
						collection.append(view)
				else:
					combine(colAttrs[1:], columnList)
		combine(attributes, [])
		return ViewCollection(collection)

	@staticmethod
	def expandUnderspecified(ldf, viewCollection):
		"""
		Given a underspecified Spec, populate the dataType and dataModel information accordingly

		Parameters
		----------
		ldf : lux.luxDataFrame.LuxDataFrame
			LuxDataFrame with underspecified context

		viewCollection : list[lux.view.View]
			List of lux.View objects that will have their underspecified Spec details filled out.
		Returns
		-------
		views: list[lux.View]
			view collection with compiled lux.View objects.
		"""		
		# TODO: copy might not be neccesary
		import copy
		views = copy.deepcopy(viewCollection)  # Preserve the original dobj
		for view in views:
			for spec in view.specLst:
				if spec.description == "?":
					spec.description = ""
				if spec.attribute:
					if (spec.dataType == ""):
						spec.dataType = ldf.dataTypeLookup[spec.attribute]
					if (spec.dataModel == ""):
						spec.dataModel = ldf.dataModelLookup[spec.attribute]
				if (spec.value!=""):
					if(isinstance(spec.value,np.datetime64)):
						# TODO: Make this more general and not specific to Year attributes
						chartTitle = pd.to_datetime(spec.value, format='%Y').year
					else:
						chartTitle = spec.value
					view.title = f"{spec.attribute} {spec.filterOp} {chartTitle}"
		return views

	@staticmethod
	def removeAllInvalid(viewCollection:ViewCollection) -> ViewCollection:
		"""
		Given an expanded view collection, remove all views that are invalid.
		Currently, the invalid views are ones that contain temporal by temporal attributes or overlapping attributes.
		Parameters
		----------
		viewCollection : list[lux.view.View]
			empty list that will be populated with specified lux.View objects.
		Returns
		-------
		views: list[lux.View]
			view collection with compiled lux.View objects.
		"""
		newVC = []

		for view in viewCollection:
			numTemporalSpecs = 0
			attributeSet = set()
			for spec in view.specLst:
				attributeSet.add(spec.attribute)
				if spec.dataType == "temporal":
					numTemporalSpecs += 1
			allDistinctSpecs = 0 == len(view.specLst) - len(attributeSet)
			if numTemporalSpecs <= 1 or allDistinctSpecs:
				newVC.append(view)

		return ViewCollection(newVC)

	@staticmethod
	def determineEncoding(ldf: LuxDataFrame,view: View):
		'''
		Populates View with the appropriate mark type and channel information based on ShowMe logic
		Currently support up to 3 dimensions or measures
		
		Parameters
		----------
		ldf : lux.luxDataFrame.LuxDataFrame
			LuxDataFrame with underspecified context
		view : lux.view.View

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
		Ndim = 0
		Nmsr = 0
		filters = []
		for spec in view.specLst:
			if (spec.value==""):
				if (spec.dataModel == "dimension"):
					Ndim += 1
				elif (spec.dataModel == "measure" and spec.attribute!="Record"):
					Nmsr += 1
			else:  # preserve to add back to specLst later
				filters.append(spec)
		# Helper function (TODO: Move this into utils)
		def lineOrBar(ldf,dimension, measure):
			dimType = dimension.dataType
			# If no aggregation function is specified, then default as average
			if (measure.aggregation==""):
				measure.aggregation = "mean"
			if (dimType == "temporal" or dimType == "oridinal"):
				return "line", {"x": dimension, "y": measure}
			else:  # unordered categorical
				# if cardinality large than 5 then sort bars
				if ldf.cardinality[dimension.attribute]>5:
					dimension.sort = "ascending"
				return "bar", {"x": measure, "y": dimension}
		

		# ShowMe logic + additional heuristics
		#countCol = Spec( attribute="count()", dataModel="measure")
		countCol = Spec( attribute="Record", aggregation="count", dataModel="measure", dataType="quantitative")
		# xAttr = view.getAttrByChannel("x") # not used as of now
		# yAttr = view.getAttrByChannel("y")
		# zAttr = view.getAttrByChannel("z")
		autoChannel={}
		if (Ndim == 0 and Nmsr == 1):
			# Histogram with Count 
			measure = view.getAttrByDataModel("measure",excludeRecord=True)[0]
			if (len(view.getAttrByAttrName("Record"))<0):
				view.specLst.append(countCol)
			# If no bin specified, then default as 10
			if (measure.binSize == 0):
				measure.binSize = 10
			autoChannel = {"x": measure, "y": countCol}
			view.xMinMax = ldf.xMinMax
			view.mark = "histogram"
		elif (Ndim == 1 and (Nmsr == 0 or Nmsr == 1)):
			# Line or Bar Chart
			# if x is unspecified
			if (Nmsr == 0):
				view.specLst.append(countCol)
			dimension = view.getAttrByDataModel("dimension")[0]
			measure = view.getAttrByDataModel("measure")[0]
			view.mark, autoChannel = lineOrBar(ldf,dimension, measure) 
		elif (Ndim == 2 and (Nmsr == 0 or Nmsr == 1)):
			# Line or Bar chart broken down by the dimension
			dimensions = view.getAttrByDataModel("dimension")
			d1 = dimensions[0]
			d2 = dimensions[1]
			if (ldf.cardinality[d1.attribute] < ldf.cardinality[d2.attribute]):
				# d1.channel = "color"
				view.removeColumnFromSpec(d1.attribute)
				dimension = d2
				colorAttr = d1
			else:
				if (d1.attribute == d2.attribute):
					view.specLst.pop(
						0)  # if same attribute then removeColumnFromSpec will remove both dims, we only want to remove one
				else:
					view.removeColumnFromSpec(d2.attribute)
				dimension = d1
				colorAttr = d2
			# Colored Bar/Line chart with Count as default measure
			if (Nmsr == 0):
				view.specLst.append(countCol)
			measure = view.getAttrByDataModel("measure")[0]
			view.mark, autoChannel = lineOrBar(ldf,dimension, measure)
			autoChannel["color"] = colorAttr
		elif (Ndim == 0 and Nmsr == 2):
			# Scatterplot
			view.xMinMax = ldf.xMinMax
			view.yMinMax = ldf.yMinMax
			view.mark = "scatter"
			autoChannel = {"x": view.specLst[0],
						   "y": view.specLst[1]}
		elif (Ndim == 1 and Nmsr == 2):
			# Scatterplot broken down by the dimension
			measure = view.getAttrByDataModel("measure")
			m1 = measure[0]
			m2 = measure[1]

			colorAttr = view.getAttrByDataModel("dimension")[0]
			view.removeColumnFromSpec(colorAttr)
			view.xMinMax = ldf.xMinMax
			view.yMinMax = ldf.yMinMax
			view.mark = "scatter"
			autoChannel = {"x": m1,
						   "y": m2,
						   "color": colorAttr}
		elif (Ndim == 0 and Nmsr == 3):
			# Scatterplot with color
			view.xMinMax = ldf.xMinMax
			view.yMinMax = ldf.yMinMax
			view.mark = "scatter"
			autoChannel = {"x": view.specLst[0],
						   "y": view.specLst[1],
						   "color": view.specLst[2]}
		if (autoChannel!={}):
			view = Compiler.enforceSpecifiedChannel(view, autoChannel)
			view.specLst.extend(filters)  # add back the preserved filters

	@staticmethod
	def enforceSpecifiedChannel(view: View, autoChannel: Dict[str,str]):
		"""
		Enforces that the channels specified in the View by users overrides the showMe autoChannels.
		
		Parameters
		----------
		view : lux.view.View
			Input View without channel specification.
		autoChannel : Dict[str,str]
			Key-value pair in the form [channel: attributeName] specifying the showMe recommended channel location.
		
		Returns
		-------
		view : lux.view.View
			View with channel specification combining both original and autoChannel specification.
		
		Raises
		------
		ValueError
			Ensures no more than one attribute is placed in the same channel.
		"""		
		resultDict = {}  # result of enforcing specified channel will be stored in resultDict
		specifiedDict = {}  # specifiedDict={"x":[],"y":[list of Dobj with y specified as channel]}
		# create a dictionary of specified channels in the given dobj
		for val in autoChannel.keys():
			specifiedDict[val] = view.getAttrByChannel(val)
			resultDict[val] = ""
		# for every element, replace with what's in specifiedDict if specified
		for sVal, sAttr in specifiedDict.items():
			if (len(sAttr) == 1):  # if specified in dobj
				# remove the specified channel from autoChannel (matching by value, since channel key may not be same)
				for i in list(autoChannel.keys()):
					if ((autoChannel[i].attribute == sAttr[0].attribute)
						and (autoChannel[i].channel==sVal)): # need to ensure that the channel is the same (edge case when duplicate Cols with same attribute name)
						autoChannel.pop(i)
						break
				sAttr[0].channel = sVal
				resultDict[sVal] = sAttr[0]
			elif (len(sAttr) > 1):
				raise ValueError("There should not be more than one attribute specified in the same channel.")
		# For the leftover channels that are still unspecified in resultDict,
		# and the leftovers in the autoChannel specification,
		# step through them together and fill it automatically.
		leftover_channels = list(filter(lambda x: resultDict[x] == '', resultDict))
		for leftover_channel, leftover_encoding in zip(leftover_channels, autoChannel.values()):
			leftover_encoding.channel = leftover_channel
			resultDict[leftover_channel] = leftover_encoding
		view.specLst = list(resultDict.values())
		return view

	@staticmethod
	# def populateWildcardOptions(ldf: LuxDataFrame) -> dict:
	def populateWildcardOptions(specLst:List[Spec],ldf: LuxDataFrame) -> dict:
		"""
		Given wildcards and constraints in the LuxDataFrame's context,
		return the list of available values that satisfies the dataType or dataModel constraints.

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
		from lux.utils.utils import convert2List

		specs = {"attributes": [], "filters": []}
		for spec in specLst:
			specOptions = []
			if spec.value == "":  # attribute
				if spec.attribute == "?":
					options = set(list(ldf.columns))  # all attributes
					if (spec.dataType != ""):
						options = options.intersection(set(ldf.dataType[spec.dataType]))
					if (spec.dataModel != ""):
						options = options.intersection(set(ldf.dataModel[spec.dataModel]))
					options = list(options)
				else:
					options = convert2List(spec.attribute)
				for optStr in options:
					if str(optStr) not in spec.exclude:
						specCopy = copy.copy(spec)
						specCopy.attribute = optStr
						specOptions.append(specCopy)
				specs["attributes"].append(specOptions)
			else:  # filters
				attrLst = convert2List(spec.attribute)
				for attr in attrLst:
					options = []
					if spec.value == "?":
						options = ldf.uniqueValues[attr]
						specInd = specLst.index(spec)
						specLst[specInd] = Spec(attribute=spec.attribute, filterOp="=", value=list(options))
					else:
						options.extend(convert2List(spec.value))
					for optStr in options:
						if str(optStr) not in spec.exclude:
							specCopy = copy.copy(spec)
							specCopy.attribute = attr
							specCopy.value = optStr
							specOptions.append(specCopy)
				specs["filters"].extend(specOptions)

		return specs
