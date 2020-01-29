from lux.dataObj.Row import Row
from lux.dataObj.Column import Column
from lux.dataset.Dataset import Dataset
from lux.utils.utils import convert2List, applyDataTransformations
from typing import List, Dict
class Compiler:
	def __init__(self):
		self.name = "Compiler"

	def __repr__(self):
		return f"<Compiler>"

	def expandUnderspecified(self, dobj):
		"""
		Given a underspecified DataObject, populate the dataType and dataModel information accordingly
		
		Parameters
		----------
		dobj : lux.dataObj.dataObj.DataObj
			Underspecified DataObj input
		
		Returns
		-------
		expandedDobj : lux.dataObj.dataObj.DataObj
			DataObj with dataType and dataModel information
		"""		
		# Automatic type conversion (only for single attributes not lists of attributes)
		import copy
		expandedDobj = copy.deepcopy(dobj)  # Preserve the original dobj

		for rcObj in expandedDobj.spec:
			if (rcObj.className == "Column" and rcObj.columnName != "?"):
				if (type(rcObj.columnName)==list and len(rcObj.columnName)==1):
					# Make `Column <['Horsepower']>` --> `Column <'Horsepower'>`
					rcObj.columnName = rcObj.columnName[0]
				if (rcObj.dataType == ""):
					rcObj.dataType = dobj.dataset.dataTypeLookup[rcObj.columnName]
				if (rcObj.dataModel == ""):
					rcObj.dataModel = dobj.dataset.dataModelLookup[rcObj.columnName]
			if (rcObj.className == "Row"):
				expandedDobj.dataset = applyDataTransformations(expandedDobj.dataset, fAttribute=rcObj.fAttribute, fVal = rcObj.fVal) 
				expandedDobj.title = f"{rcObj.fAttribute}={rcObj.fVal}"
		return expandedDobj
	def enumerateCollection(self, dobj):
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
		# Get all the column and row object, assign the attribute names to variables
		colSpecs = sorted(list(filter(lambda x: x.className == "Column", dobj.spec)), key=lambda x: x.channel) # sort by channel x,y,z
		rowSpecs = list(filter(lambda x: x.className == "Row", dobj.spec))
		colAttrs = []
		rowList = []
		fAttr = ''
		for colSpec in colSpecs:
			colAttrs.append(Compiler.populateOptions(dobj, colSpec))
		if len(rowSpecs) > 0:
			rowList = Compiler.populateOptions(dobj, rowSpecs[0])  # populate rowvals with all unique possibilities
		if all(len(attrs) <= 1 for attrs in colAttrs) and len(rowList) <= 1:  # changed condition to check if every column attribute has at least one attribute
			# If DataObj does not represent a collection, return False.
			return False
		else:
			collection = self.generateCollection(colAttrs, rowList, dobj)
			return collection
	@staticmethod
	def populateOptions(dobj, rowCol):
		"""
		Given a row or column object, return the list of available values that satisfies the dataType or dataModel constraints
		
		Parameters
		----------
		dobj : lux.dataObj.dataObj.DataObj
			[description]
		rowCol : Row or Column Object
			Input row or column object with wildcard or list
		
		Returns
		-------
		rcOptions: List
			List of expanded Column or Row objects 
		"""		
		import copy
		if rowCol.className == "Column":
			if rowCol.columnName == "?":
				options = set(dobj.dataset.attrList)  # all attributes
				if (rowCol.dataType != ""):
					options = options.intersection(set(dobj.dataset.dataType[rowCol.dataType]))
				if (rowCol.dataModel != ""):
					options = options.intersection(set(dobj.dataset.dataModel[rowCol.dataModel]))
				options = list(options)
			else:
				options = convert2List(rowCol.columnName)
			rcOptions = []
			for optStr in options:
				rcCopy = copy.copy(rowCol)
				rcCopy.columnName = optStr
				rcOptions.append(rcCopy)
		elif rowCol.className == "Row":
			rcOptions = []
			fAttrLst = convert2List(rowCol.fAttribute)
			for fAttr in fAttrLst:
				if rowCol.fVal == "?":
					options = dobj.dataset.df[fAttr].unique()
				else:
					options = convert2List(rowCol.fVal)	
				for optStr in options:
					rcCopy = copy.copy(rowCol)
					rcCopy.fAttribute = fAttr
					rcCopy.fVal = optStr
					rcOptions.append(rcCopy)
		return rcOptions

	def generateCollection(self, colAttrs: List[Row], rowList: List[Column], dobj):  # [[colA,colB],[colC,colD]] -> [[colA,colC],[colA,colD],[colB,colC],[colB,colD]]								
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
		from lux.dataObj.dataObj import DataObj
		from lux.dataObj.DataObjCollection import DataObjCollection
		collection = []
		# generate combinations of column attributes recursively by continuing to accumulate attributes for len(colAtrr) times
		def combine(colAttrs, accum):
			last = (len(colAttrs) == 1)
			n = len(colAttrs[0])
			for i in range(n):
				columnList = accum + [colAttrs[0][i]]
				if last:
					if len(rowList) > 0: # if we have rows, generate combinations for each row.
						for row in rowList:
							transformedDataset = applyDataTransformations(dobj.dataset, row.fAttribute, row.fVal)  # rename?
							specLst = columnList + [row]
							dataObj = DataObj(transformedDataset, specLst, title=f"{row.fAttribute}={row.fVal}")
							collection.append(dataObj)
					else:
						dataObj = DataObj(dobj.dataset, columnList)
						collection.append(dataObj)
				else:
					combine(colAttrs[1:], columnList)

		combine(colAttrs, [])
		return DataObjCollection(collection)

	@classmethod
	def determineEncoding(cls, dobj):
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
		# TODO: possibly implement chart alternatives as a list of possible encodings

		# Count number of measures and dimensions
		Ndim = 0
		Nmsr = 0
		rowLst = []
		for spec in dobj.spec:
			if (spec.className == "Column"):
				if (spec.dataModel == "dimension"):
					Ndim += 1
				elif (spec.dataModel == "measure"):
					Nmsr += 1
			if (spec.className == "Row"):  # preserve to add back to dobj later
				rowLst.append(spec)
		# Helper function (TODO: Move this into utils)
		def lineOrBar(dimension, measure):
			dimType = dimension.dataType
			if (dimType == "date" or dimType == "oridinal"):
				# chart = LineChart(dobj)
				return "line", {"x": dimension, "y": measure}
			else:  # unordered categorical
				# chart = BarChart(dobj)
				return "bar", {"x": measure, "y": dimension}
		# TODO: if cardinality large than 6 then sort bars

		# ShowMe logic + additional heuristics
		countCol = Column("count()", dataModel="measure")
		xAttr = dobj.getObjFromChannel("x")
		yAttr = dobj.getObjFromChannel("y")
		zAttr = dobj.getObjFromChannel("z")
		autoChannel={}
		if (Ndim == 0 and Nmsr == 1):
			# Histogram with Count on the y axis
			measure = dobj.getObjByDataModel("measure")[0]
			dobj.spec.append(countCol)
			# measure.channel = "x"
			autoChannel = {"x": measure, "y": countCol}
			dobj.mark = "histogram"
		elif (Ndim == 1 and (Nmsr == 0 or Nmsr == 1)):
			# Line or Bar Chart
			# if x is unspecified
			if (Nmsr == 0):
				dobj.spec.append(countCol)
			dimension = dobj.getObjByDataModel("dimension")[0]
			measure = dobj.getObjByDataModel("measure")[0]
			# measure.channel = "x"
			dobj.mark, autoChannel = lineOrBar(dimension, measure)
		elif (Ndim == 2 and (Nmsr == 0 or Nmsr == 1)):
			# Line or Bar chart broken down by the dimension
			dimensions = dobj.getObjByDataModel("dimension")
			d1 = dimensions[0]
			d2 = dimensions[1]
			if (dobj.dataset.cardinality[d1.columnName] < dobj.dataset.cardinality[d2.columnName]):
				# d1.channel = "color"
				dobj.removeColumnFromSpec(d1.columnName)
				dimension = d2
				colorAttr = d1
			else:
				if (d1.columnName == d2.columnName):
					dobj.spec.pop(
						0)  # if same attribute then removeColumnFromSpec will remove both dims, we only want to remove one
				else:
					dobj.removeColumnFromSpec(d2.columnName)
				dimension = d1
				colorAttr = d2
			# Colored Bar/Line chart with Count as default measure
			if (Nmsr == 0):
				dobj.spec.append(countCol)
			measure = dobj.getObjByDataModel("measure")[0]
			dobj.mark, autoChannel = lineOrBar(dimension, measure)
			autoChannel["color"] = colorAttr
		elif (Ndim == 0 and Nmsr == 2):
			# Scatterplot
			dobj.mark = "scatter"
			autoChannel = {"x": dobj.spec[0],
						   "y": dobj.spec[1]}
		elif (Ndim == 1 and Nmsr == 2):
			# Scatterplot broken down by the dimension
			measure = dobj.getObjByDataModel("measure")
			m1 = measure[0]
			m2 = measure[1]

			colorAttr = dobj.getObjByDataModel("dimension")[0]
			dobj.removeColumnFromSpec(colorAttr)

			dobj.mark = "scatter"
			autoChannel = {"x": m1,
						   "y": m2,
						   "color": colorAttr}
		elif (Ndim == 0 and Nmsr == 3):
			# Scatterplot with color
			dobj.mark = "scatter"
			autoChannel = {"x": dobj.spec[0],
						   "y": dobj.spec[1],
						   "color": dobj.spec[2]}
		if (autoChannel!={}):
			dobj = cls.enforceSpecifiedChannel(dobj, autoChannel) 
			dobj.spec.extend(rowLst)  # add back the preserved row objects
		return dobj

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