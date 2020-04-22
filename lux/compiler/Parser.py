from lux.context.Spec import Spec
from lux.luxDataFrame.LuxDataframe import LuxDataFrame
class Parser:
	@staticmethod
	def parse(ldf: LuxDataFrame) -> None:
		'''
		Parse takes the description from the input Spec and assign it into the appropriate spec.attribute, spec.filterOp, and spec.value
		'''
		import re
		parsedContext = ldf.getContext()
		newContext = []
		#checks for and converts users' string inputs into lux specifications
		for s in parsedContext:
			validValues = []

			if type(s) is list:
				validValues = []
				for v in s:
					if type(v) is str and v in ldf.columns:
						validValues.append(v)
				tempSpec = Spec(attribute = validValues, type = "attribute")
				newContext.append(tempSpec)
			elif type(s) is str:
				#case where user specifies a filter
				if "=" in s:
					eqInd = s.index("=")
					var = s[0:eqInd]
					if "|" in s:
						values = s[eqInd+1:].split("|")
						for v in values:
							if v in ldf[var].unique():
								validValues.append(v)
					else:
						validValues = s[eqInd+1:]
					if var in ldf.columns:
						tempSpec = Spec(attribute = var, filterOp = "=", value = validValues, type = "value")
						newContext.append(tempSpec)
				#case where user specifies a variable
				else:
					if "|" in s:
						values = s.split("|")
						for v in values:
							if v in ldf.columns:
								validValues.append(v)
					else:
						validValues = s
					tempSpec = Spec(attribute = validValues, type = "attribute")
					newContext.append(tempSpec)
			elif type(s) is Spec:
				newContext.append(s)
		parsedContext = newContext
		ldf.context = newContext

		for spec in parsedContext:
			if (spec.description):
				if (spec.description in ldf.columns or spec.description == "?"):# if spec.description in the list of attributes
					spec.attribute = spec.description
				elif any(ext in [">","<","="] for ext in spec.description): # spec.description contain ">","<". or "="
					# then parse it and assign to spec.attribute, spec.filterOp, spec.values
					spec.filterOp = re.findall(r'/.*/>|=|<|>=|<=|!=', spec.description)[0]
					splitDescription = spec.description.split(spec.filterOp)
					spec.attribute = splitDescription[0]
					spec.value = splitDescription[1]
				else: # then it is probably a value 
					spec.values = spec.description

		ldf.context = parsedContext
		Parser.populateOptions(ldf)
		
	@staticmethod
	def populateOptions(ldf: LuxDataFrame) -> None:
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
		from lux.utils.utils import convert2List
		for spec in ldf.context:
			specOptions = []
			if  spec.value=="" : # attribute
				if spec.attribute == "?":
					options = set(ldf.attrList)  # all attributes
					if (spec.dataType != ""):
						options = options.intersection(set(ldf.dataType[spec.dataType]))
					if (spec.dataModel != ""):
						options = options.intersection(set(ldf.dataModel[spec.dataModel]))
					options = list(options)
				else:
					options = convert2List(spec.attribute)
				for optStr in options:
					specCopy = copy.copy(spec)
					specCopy.attribute = optStr
					specOptions.append(specCopy)
				ldf.cols.append(specOptions)
			else:
				# if spec.attribute:
				# 	attrLst = convert2List(spec.attribute)
				# else:
				# 	attrLst = convert2List(spec.attributeGroup)
				attrLst = convert2List(spec.attribute)
				for attr in attrLst:
					if spec.value == "?":
						options = ldf.uniqueValues[attr]
						specInd = ldf.context.index(spec)
						ldf.context[specInd] = Spec(attribute = spec.attribute, filterOp = "=", value = list(options))
					else:
						options = convert2List(spec.value)
					for optStr in options:
						specCopy = copy.copy(spec)
						specCopy.attribute = attr
						specCopy.value = optStr
						specOptions.append(specCopy)
				# ldf.rows.append(specOptions)
				ldf.rows = specOptions
