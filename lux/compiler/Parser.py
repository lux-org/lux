import lux
class Parser:
	'''
	DONE
	lux.setContext("Horsepower")
	--> lux.Spec(attribute = "Horsepower", type= "attribute")

	DONE
	lux.setContext("Horsepower", lux.Spec("MilesPerGal",channel="x"))
		--> [lux.Spec(attribute ="Horsepower", type= "attribute"), lux.Spec(attribute ="MilesPerGal", type= "attribute",channel="x")]

	DONE
	lux.setContext("Horsepower","Origin=USA")
		--> [lux.Spec(attribute ="Horsepower", type= "attribute"), lux.Spec(attribute ="Origin", fOp = "=", value ="USA", type= "value")]

	lux.setContext("Horsepower","USA")
		--> [lux.Spec(attribute ="Horsepower", type= "attribute"), lux.Spec(attribute ="Origin", fOp = "=", value ="USA", type= "value")]

	lux.setContext("Horsepower","Origin=?")
		-->[lux.Spec(attribute ="Horsepower", type= " attribute"), lux.Spec(attribute ="Origin", fOp = "=", value ="?", type= "valueGroup")]

		Then populateOptions compiles "?" into :
		-->[[lux.Spec(attr ="Horsepower", type= " attribute"), lux.Spec(fAttr = "Origin", fOp = "=", fVal="USA", type= "value")],
			[lux.Spec(attr ="Horsepower", type= "attribute"), lux.Spec(fAttr = "Origin", fOp = "=", fVal="UK", type= "value")],
			[lux.Spec(attr ="Horsepower", type= "attribute"), lux.Spec(fAttr = "Origin", fOp = "=", fVal="Japan", type= "value")] ]

	lux.setContext("Horsepower","Origin=USA/Japan")
		--> [lux.Spec(attribute ="Horsepower", type= "attribute"), lux.Spec(attribute ="Origin", fOp = "=", value =["USA","Japan"], type= "valueGroup")]

	DONE
	lux.setContext(["Horsepower","MPG","Acceleration"],"Origin")
	lux.setContext("Horsepower/MPG/Acceleration", "Origin")
		--> [lux.Spec(attr= ["Horsepower","MPG","Acceleration"], type= "attributeGroup")]
	'''

	@staticmethod
	# def parse(context: list[lux.Spec]):
	def parse(ldf):
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
				tempSpec = lux.Spec(attribute = validValues, type = "attribute")
				newContext.append(tempSpec)
			if type(s) is str:
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
						tempSpec = lux.Spec(attribute = var, filterOp = "=", value = validValues, type = "value")
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
					tempSpec = lux.Spec(attribute = validValues, type = "attribute")
					newContext.append(tempSpec)
			elif type(s) is lux.Spec:
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

			#after parsing:
			if spec.attribute == "?" or isinstance(spec.attribute,list):
				spec.type = "attributeGroup"
			if spec.value == "?" or isinstance(spec.value,list):
				spec.type = "valueGroup"

		ldf.context = parsedContext
		Parser.populateOptions(ldf)
		
	@staticmethod
	# def populateOptions(ldf: LuxDataFrame):
	def populateOptions(ldf):
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
			if "attribute" in spec.type:
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
					specCopy.type = "attribute"
					specOptions.append(specCopy)
				ldf.cols.append(specOptions)
			elif "value" in spec.type:
				# if spec.attribute:
				# 	attrLst = convert2List(spec.attribute)
				# else:
				# 	attrLst = convert2List(spec.attributeGroup)
				attrLst = convert2List(spec.attribute)
				for attr in attrLst:
					if spec.value == "?":
						options = ldf.uniqueValues[attr]
						specInd = ldf.context.index(spec)
						ldf.context[specInd] = lux.Spec(attribute = spec.attribute, filterOp = "=", value = list(options), type = "valueGroup")
					else:
						options = convert2List(spec.value)
					for optStr in options:
						specCopy = copy.copy(spec)
						specCopy.attribute = attr
						specCopy.value = optStr
						specCopy.type = "value"
						specOptions.append(specCopy)
				# ldf.rows.append(specOptions)
				ldf.rows = specOptions
