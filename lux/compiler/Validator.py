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

		-->[[lux.Spec(attr ="Horsepower", type= "attribute"), lux.Spec(fAttr = "Origin", fOp = "=", fVal="USA", type= "value")],
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
			if spec.attribute :
				spec.type = "attribute"
			elif spec.value :
				spec.type = "value"
			elif spec.attributeGroup:
				spec.type = "attributeGroup"
			elif spec.valueGroup:
				spec.type = "valueGroup"
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
			checkAttrExists = spec.attribute in luxDataFrame.attrList
			checkValExists = spec.value in uniqueVals
			checkAttrExistsGroup = all(attr in luxDataFrame.attrList for attr in spec.attributeGroup)
			checkValExistsGroup = all(existsInDF(val,uniqueVals) for val in spec.valueGroup)
			
			if spec.attribute and not checkAttrExists:
				printWarning = True
			elif spec.value and not checkValExists:
				printWarning = True
			elif spec.attributeGroup and not (spec.attributeGroup=="?" or checkAttrExistsGroup):
				printWarning = True
			elif spec.valueGroup and not (spec.valueGroup=="?" or checkValExistsGroup):
				printWarning = True

		if printWarning:
			#print warning
			raise ValueError("Input spec is inconsistent with DataFrame.")
		



		# lux.setContext(lux.Spec(attr = "Horsepower"))
		# lux.setContext(lux.Spec(attr = "A")) --> Warning

