class Parser:
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

	@staticmethod
	# def parse(context: list[lux.Spec]):
	def parse(ldf):
		'''
		Parse takes the description from the input Spec and assign it into the appropriate spec.attribute, spec.filterOp, and spec.value
		'''
		import re
		parsedContext = ldf.getContext()
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
			if spec.attribute:
				spec.type = "attribute"
			if spec.value:
				spec.type = "value"
			if spec.attribute == "?" or isinstance(spec.attribute,list):
				spec.type = "attributeGroup"
			if spec.value == "?" or isinstance(spec.value,list):
				spec.type = "valueGroup"
		ldf.context = parsedContext

		