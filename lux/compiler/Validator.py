from lux.utils.utils import convert2List

class Validator:
	'''
	lux.setContext("Horsepower")
	--> lux.Spec(attr = "Horsepower", type= "attribute")

	lux.setContext("Horsepower", lux.Spec("MilesPerGal",channel="x"))
		--> [lux.Spec(attr ="Horsepower", type= "attribute"), lux.Spec(attr ="MilesPerGal", type= "attribute",channel="x")]

	lux.setContext("Horsepower","Origin=USA")
		--> [lux.Spec(attr ="Horsepower", type= "attribute"), lux.Spec(fAttr = "Origin", fOp = "=", fVal="USA", type= "value")]

	lux.setContext("Horsepower","USA")
		--> [lux.Spec(attr ="Horsepower", type= "attribute"), lux.Spec(fAttr = "Origin", fOp = "=", fVal="USA", type= "value")]

	lux.setContext("Horsepower","Origin=?")
		--> [lux.Spec(attr ="Horsepower", type= "attribute"), lux.Spec(fAttr = "Origin", fOp = "=", fVal="?", type= "valueGroup")]

		-->[[lux.Spec(attr ="Horsepower", type= " attribute"), lux.Spec(fAttr = "Origin", fOp = "=", fVal="USA", type= "value")],
			[lux.Spec(attr ="Horsepower", type= "attribute"), lux.Spec(fAttr = "Origin", fOp = "=", fVal="UK", type= "value")],
			[lux.Spec(attr ="Horsepower", type= "attribute"), lux.Spec(fAttr = "Origin", fOp = "=", fVal="Japan", type= "value")] ]

	lux.setContext(["Horsepower","MPG","Acceleration"])
		--> [lux.Spec(attrGroup = ["Horsepower","MPG","Acceleration"], type= "attributeGroup")]
	'''
	def __init__(self):
		self.name = "Validator"

	def __repr__(self):
		return f"<Validator>"

	@staticmethod
	def parseSpec(luxDataFrame):
		# do parsing ....
		# after parsing
		context = luxDataFrame.getContext()
		for spec in context:
			if spec.attribute:
				spec.type = "attribute"
			if spec.value:
				spec.type = "value"
			if spec.attribute == "?" or isinstance(spec.attribute,list):
				spec.type = "attributeGroup"
			if spec.value == "?" or isinstance(spec.value,list):
				spec.type = "valueGroup"

		Validator.populateOptions(luxDataFrame)


	@staticmethod
	def validateSpec(luxDataFrame):
		def existsInDF(value,uniqueValues):
			return any(value in vals for vals in uniqueValues)
		# 1. Parse all string specification into Spec objects (nice-to-have)
		# 2. Validate that the parsed specification is corresponds to the content in the LuxDataframe.
		context = luxDataFrame.getContext()
		uniqueVals = luxDataFrame.uniqueValues
		printWarning = False
		for spec in context:
			if isinstance(spec.attribute,list):
				checkAttrExistsGroup = all(attr in luxDataFrame.attrList for attr in spec.attribute)
				if spec.attribute and not (spec.attribute == "?" or checkAttrExistsGroup):
					printWarning = True
			else:
				checkAttrExists = spec.attribute in luxDataFrame.attrList
				if spec.attribute and not checkAttrExists:
					printWarning = True

			if isinstance(spec.value, list):
				checkValExistsGroup = all(existsInDF(val, uniqueVals) for val in spec.value)
				if spec.value and not (spec.value == "?" or checkValExistsGroup):
					printWarning = True
			else:
				checkValExists = spec.axis and spec.value in uniqueVals[spec.axis]
				if spec.value and not checkValExists:
					printWarning = True

		if printWarning:
			#print warning
			raise ValueError("Input spec is inconsistent with DataFrame.")

		# lux.setContext(lux.Spec(attr = "Horsepower"))
		# lux.setContext(lux.Spec(attr = "A")) --> Warning

	@staticmethod
	def populateOptions(luxDataFrame):
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
		for spec in luxDataFrame.context:
			specOptions = []
			if "attribute" in spec.type:
				if spec.attribute == "?":
					options = set(luxDataFrame.attrList)  # all attributes
					if (spec.dataType != ""):
						options = options.intersection(set(luxDataFrame.dataType[spec.dataType]))
					if (spec.dataModel != ""):
						options = options.intersection(set(luxDataFrame.dataModel[spec.dataModel]))
					options = list(options)
				else:
					options = convert2List(spec.attribute)
				for optStr in options:
					specCopy = copy.copy(spec)
					specCopy.attribute = optStr
					specCopy.type = "attribute"
					specOptions.append(specCopy)
				luxDataFrame.cols.append(specOptions)
			elif "value" in spec.type:
				# if spec.attribute:
				# 	attrLst = convert2List(spec.attribute)
				# else:
				# 	attrLst = convert2List(spec.attributeGroup)
				attrLst = convert2List(spec.axis)
				for attr in attrLst:
					if spec.value == "?":
						options = luxDataFrame.uniqueValues[attr]
					else:
						options = convert2List(spec.value)
					for optStr in options:
						specCopy = copy.copy(spec)
						specCopy.axis = attr
						specCopy.value = optStr
						specCopy.type = "value"
						specOptions.append(specCopy)
				# luxDataFrame.rows.append(specOptions)
				luxDataFrame.rows = specOptions