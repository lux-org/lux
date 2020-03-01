from lux.dataObj.Row import Row
from lux.dataObj.Column import Column
from lux.dataset.Dataset import Dataset
from lux.utils.utils import convert2List, applyDataTransformations
from typing import List, Dict

from lux.view.ViewCollection import ViewCollection
class Compiler:
	def __init__(self):
		self.name = "Compiler"

	def __repr__(self):
		return f"<Compiler>"
	@staticmethod
	def compile(ldf):
		# 1. If the DataObj represent a collection, then compile it into a collection. Otherwise, return False
		# Input: DataObj --> Output: DataObjCollection/False
		# if (enumerateCollection):
		ldf = Compiler.enumerateCollection(ldf) 
		# else:
		# 	dataObjCollection = False
		# 2. For every DataObject in the DataObject Collection, expand underspecified
		# Output : DataObj/DataObjectCollection
		
		# compiledCollection = []
		#TODO make viewCollection iterable
		for view in ldf.viewCollection.collection: # these two function calls directly mutates the View object
			Compiler.expandUnderspecified(ldf, view)  # autofill data type/model information
			Compiler.determineEncoding(ldf, view)  # autofill viz related information			
			# compiledCollection.append(ldf.getView())
		# print ("uncompiled:",dataObj)
		# print ("compiled:",compiled)
		# ldf.setView()
		# self.compiled.collection = compiledCollection  # return DataObjCollection
	@staticmethod
	def expandUnderspecified(ldf, view):
		"""
		Given a underspecified Spec, populate the dataType and dataModel information accordingly
		
		Parameters
		----------
		dobj : lux.dataObj.dataObj.DataObj
			Underspecified DataObj input
		
		Returns
		-------
		expandedDobj : lux.dataObj.dataObj.DataObj
			DataObj with dataType and dataModel information
		"""		
		# TODO: copy might not be neccesary
		import copy
		expandedContext = copy.deepcopy(ldf.viewCollection)  # Preserve the original dobj

		for spec in expandedContext:

			# expand spec
			# if (spec.type in "attributeGroup" and len(spec.attributeGroup) == 1): # case when attribute group has only one element
			# 	spec.attribute = spec.attributeGroup[0]
			if (spec.dataType == ""):
				spec.dataType = ldf.dataTypeLookup[spec.attribute]
			if (spec.dataModel == ""):
				spec.dataModel = ldf.dataModelLookup[spec.attribute]

		ldf.setView(expandedContext)
	@staticmethod
	def enumerateCollection(ldf):
		"""
		Given a partial specification, enumerate items in the collection via populateOption, 
		then call the recursive generateCollection to iterate over the resulting list combinations.
		
		Parameters
		----------
		dobj : lux.dataObj.dataObj.DataObj
			Input DataObject
		
		Returns
		-------
		collection: lux.dataObj.dataObj.DataObjectCollection
			Resulting DataObjectCollection
		"""		
		# vcol = ViewCollection([]) #placeholder
		# TODO: compute the views for the collection
		# Get all the column and row object, assign the attribute names to variables
		specs = sorted(list(filter(lambda x: x.attribute or x.attributeGroup, ldf.spec)), key=lambda x: x.channel) # sort by channel x,y,z
		operations = list(filter(lambda x: x.filterOp, ldf.spec))
		attrs = []
		ops = []
		for spec in specs:
			attrs.append(Compiler.populateOptions(ldf, spec))
		if len(operations) > 0:
			ops = Compiler.populateOptions(ldf, operations)  # populate rowvals with all unique possibilities
		if all(len(attrs) <= 1 for attr in attrs) and len(ops) <= 1:
			# changed condition to check if every column attribute has at least one attribute
			# If DataObj does not represent a collection, return False.
			pass
		else:
			underspecifiedVcol = Compiler.generateCollection(attrs, ops, ldf)
			ldf.viewCollection = underspecifiedVcol

		return ldf

	@staticmethod
	def generateCollection(attrs: List[Row], ops: List[Column], ldf):  # [[colA,colB],[colC,colD]] -> [[colA,colC],[colA,colD],[colB,colC],[colB,colD]]
		"""
		Generates combinations for visualization collection given a list of row and column values

		Parameters
		----------
		colAttrs : List
			List of 
		dobj : lux.dataObj.dataObj.DataObj
			Partial DataObj input

		Returns
		-------
		lux.dataObj.DataObjCollection
			Resulting DataObjectCollection
		"""		
		from lux.compiler.View import View
		# from lux.dataObj.DataObjCollection import DataObjCollection
		# collection = []
		collection = []
		# TODO: generate combinations of column attributes recursively by continuing to accumulate attributes for len(colAtrr) times
		def combine(colAttrs, accum):
			last = (len(colAttrs) == 1)
			n = len(colAttrs[0])
			for i in range(n):
				columnList = accum + [colAttrs[0][i]]
				if last:
					if len(ops) > 0: # if we have rows, generate combinations for each row.
						for row in ops:
							#transformedDataset = applyDataTransformations(ldf, row.fAttribute, row.fVal)  # rename?
							specLst = columnList + [row]
							#dataObj = DataObj(transformedDataset, specLst, title=f"{row.fAttribute}={row.fVal}")
							view = View(specLst,title=f"{row.fAttribute}={row.fVal}")
							collection.append(view)
					else:
						view = View(columnList)
						collection.append(view)
				else:
					combine(colAttrs[1:], columnList)

		combine(attrs, [])
		return ViewCollection(collection)

	@staticmethod
	def determineEncoding(ldf,view):
		'''
		Populates DataObject with the appropriate mark type and channel information based on ShowMe logic
		Currently support up to 3 dimensions or measures
		
		Parameters
		----------
		dobj : lux.dataObj.dataObj.DataObj
			DataObj input

		Returns
		-------
		dobj : lux.dataObj.dataObj.DataObj
			output DataObj with `mark` and `channel` specified

		Notes
		-----
		Implementing automatic encoding from Tableau's VizQL
		Mackinlay, J. D., Hanrahan, P., & Stolte, C. (2007).
		Show Me: Automatic presentation for visual analysis.
		IEEE Transactions on Visualization and Computer Graphics, 13(6), 1137–1144.
		https://doi.org/10.1109/TVCG.2007.70594
		'''
		# TODO: Directly mutate view
		# Count number of measures and dimensions
		# Ndim = 0
		# Nmsr = 0
		# rowLst = []
		# for spec in dobj.spec:
		# 	if (spec.className == "Column"):
		# 		if (spec.dataModel == "dimension"):
		# 			Ndim += 1
		# 		elif (spec.dataModel == "measure"):
		# 			Nmsr += 1
		# 	if (spec.className == "Row"):  # preserve to add back to dobj later
		# 		rowLst.append(spec)
		# # Helper function (TODO: Move this into utils)
		# def lineOrBar(dimension, measure):
		# 	dimType = dimension.dataType
		# 	if (dimType == "date" or dimType == "oridinal"):
		# 		# chart = LineChart(dobj)
		# 		return "line", {"x": dimension, "y": measure}
		# 	else:  # unordered categorical
		# 		# chart = BarChart(dobj)
		# 		return "bar", {"x": measure, "y": dimension}
		# # TODO: if cardinality large than 6 then sort bars

		# # ShowMe logic + additional heuristics
		# countCol = Column("count()", dataModel="measure")
		# xAttr = dobj.getObjFromChannel("x")
		# yAttr = dobj.getObjFromChannel("y")
		# zAttr = dobj.getObjFromChannel("z")
		# autoChannel={}
		# if (Ndim == 0 and Nmsr == 1):
		# 	# Histogram with Count on the y axis
		# 	measure = dobj.getObjByDataModel("measure")[0]
		# 	dobj.spec.append(countCol)
		# 	# measure.channel = "x"
		# 	autoChannel = {"x": measure, "y": countCol}
		# 	dobj.mark = "histogram"
		# elif (Ndim == 1 and (Nmsr == 0 or Nmsr == 1)):
		# 	# Line or Bar Chart
		# 	# if x is unspecified
		# 	if (Nmsr == 0):
		# 		dobj.spec.append(countCol)
		# 	dimension = dobj.getObjByDataModel("dimension")[0]
		# 	measure = dobj.getObjByDataModel("measure")[0]
		# 	# measure.channel = "x"
		# 	dobj.mark, autoChannel = lineOrBar(dimension, measure)
		# elif (Ndim == 2 and (Nmsr == 0 or Nmsr == 1)):
		# 	# Line or Bar chart broken down by the dimension
		# 	dimensions = dobj.getObjByDataModel("dimension")
		# 	d1 = dimensions[0]
		# 	d2 = dimensions[1]
		# 	if (dobj.dataset.cardinality[d1.columnName] < dobj.dataset.cardinality[d2.columnName]):
		# 		# d1.channel = "color"
		# 		dobj.removeColumnFromSpec(d1.columnName)
		# 		dimension = d2
		# 		colorAttr = d1
		# 	else:
		# 		if (d1.columnName == d2.columnName):
		# 			dobj.spec.pop(
		# 				0)  # if same attribute then removeColumnFromSpec will remove both dims, we only want to remove one
		# 		else:
		# 			dobj.removeColumnFromSpec(d2.columnName)
		# 		dimension = d1
		# 		colorAttr = d2
		# 	# Colored Bar/Line chart with Count as default measure
		# 	if (Nmsr == 0):
		# 		dobj.spec.append(countCol)
		# 	measure = dobj.getObjByDataModel("measure")[0]
		# 	dobj.mark, autoChannel = lineOrBar(dimension, measure)
		# 	autoChannel["color"] = colorAttr
		# elif (Ndim == 0 and Nmsr == 2):
		# 	# Scatterplot
		# 	dobj.mark = "scatter"
		# 	autoChannel = {"x": dobj.spec[0],
		# 				   "y": dobj.spec[1]}
		# elif (Ndim == 1 and Nmsr == 2):
		# 	# Scatterplot broken down by the dimension
		# 	measure = dobj.getObjByDataModel("measure")
		# 	m1 = measure[0]
		# 	m2 = measure[1]

		# 	colorAttr = dobj.getObjByDataModel("dimension")[0]
		# 	dobj.removeColumnFromSpec(colorAttr)

		# 	dobj.mark = "scatter"
		# 	autoChannel = {"x": m1,
		# 				   "y": m2,
		# 				   "color": colorAttr}
		# elif (Ndim == 0 and Nmsr == 3):
		# 	# Scatterplot with color
		# 	dobj.mark = "scatter"
		# 	autoChannel = {"x": dobj.spec[0],
		# 				   "y": dobj.spec[1],
		# 				   "color": dobj.spec[2]}
		# if (autoChannel!={}):
		# 	dobj = Compiler.enforceSpecifiedChannel(dobj, autoChannel) 
		# 	dobj.spec.extend(rowLst)  # add back the preserved row objects
		pass

	@staticmethod
	def enforceSpecifiedChannel(dobj, autoChannel: Dict[str,str]):
		"""
		Enforces that the channels specified in the DataObj by users overrides the showMe autoChannels
		
		Parameters
		----------
		dobj : lux.dataObj.dataObj.DataObj
			Input DataObject without channel specification
		autoChannel : Dict[str,str]
			Key-value pair in the form [channel: attributeName] specifying the showMe recommended channel location
		
		Returns
		-------
		dobj : lux.dataObj.dataObj.DataObj
			Input DataObject with channel specification combining both original and autoChannel specification
		
		Raises
		------
		ValueError
			Ensures no more than one attribute is placed in the same channel
		"""		
		resultDict = {}  # result of enforcing specified channel will be stored in resultDict
		specifiedDict = {}  # specifiedDict={"x":[],"y":[list of Dobj with y specified as channel]}
		# create a dictionary of specified channels in the given dobj
		for val in autoChannel.keys():
			specifiedDict[val] = dobj.getObjFromChannel(val)
			resultDict[val] = ""
		# for every element, replace with what's in specifiedDict if specified
		for sVal, sAttr in specifiedDict.items():
			if (len(sAttr) == 1):  # if specified in dobj
				# remove the specified channel from autoChannel (matching by value, since channel key may not be same)
				for i in list(autoChannel.keys()):
					if ((autoChannel[i].columnName == sAttr[0].columnName) 
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
		dobj.spec = list(resultDict.values())
		return dobj