from lux.context.Spec import Spec
from lux.luxDataFrame.LuxDataframe import LuxDataFrame
class Parser:
	"""
	The parser takes in the user's input context specification,
	then generates the Lux internal specification through lux.Spec

	Methods
    -------
	parse
	populateWildcardOptions

	"""	
	@staticmethod
	def parse(ldf: LuxDataFrame) -> None:
		"""
		Given the string description from the input Spec,
		assign the appropriate spec.attribute, spec.filterOp, and spec.value
		
		Parameters
		----------
		ldf : LuxDataFrame
			LuxDataFrame with fully specified context consisting of lux.Spec objects
		
		Examples
        --------
		>>> ldf.context = ["Horsepower", "Origin=USA"]
		>>> ldf.context
		"""		
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
							if v in ldf.uniqueValues[var]:
								validValues.append(v)
					else:
						validValues = s[eqInd+1:]
					if var in ldf.columns or var in ldf.attrList:
						tempSpec = Spec(attribute = var, filterOp = "=", value = validValues, type = "value")
						newContext.append(tempSpec)
				#case where user specifies a variable
				else:
					if "|" in s:
						values = s.split("|")
						for v in values:
							if v in ldf.columns or v in ldf.attrList:
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
				if ((spec.description in ldf.columns or spec.description in ldf.attrList) or spec.description == "?"):# if spec.description in the list of attributes
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
		Parser.populateWildcardOptions(ldf)
		
	@staticmethod
	def populateWildcardOptions(ldf: LuxDataFrame) -> None:
		"""
		Given wildcards and constraints in the LuxDataFrame's context, 
		return the list of available values that satisfies the dataType or dataModel constraints
		
		Parameters
		----------
		ldf : LuxDataFrame
			LuxDataFrame with row or cols populated with available wildcard options
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
			else: # filters
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
				ldf.rows = specOptions
