from lux.utils.utils import convert2List
# from ..luxDataFrame.LuxDataframe import LuxDataFrame

class Validator:
	def __init__(self):
		self.name = "Validator"

	def __repr__(self):
		return f"<Validator>"

	@staticmethod
	# def validateSpec(ldf: LuxDataFrame):
	def validateSpec(ldf):
		Validator.populateOptions(ldf)
		def existsInDF(value,uniqueValues):
			return any(value in vals for vals in uniqueValues)
		# 1. Parse all string specification into Spec objects (nice-to-have)
		# 2. Validate that the parsed specification is corresponds to the content in the LuxDataframe.
		context = ldf.getContext()
		uniqueVals = ldf.uniqueValues
		printWarning = False
		for spec in context:
			if ((spec.attribute and spec.attribute == "?") or (spec.value and spec.value=="?")):
				continue
			if isinstance(spec.attribute,list):
				checkAttrExistsGroup = all(attr in ldf.attrList for attr in spec.attribute)
				if spec.attribute and not checkAttrExistsGroup:
					printWarning = True
			else:
					checkAttrExists = spec.attribute in ldf.attrList
					if spec.attribute and not checkAttrExists:
						printWarning = True

					checkValExists = spec.attribute and spec.value in uniqueVals[spec.attribute]
					if spec.value and not checkValExists:
						printWarning = True
			
			if isinstance(spec.value, list):
					checkValExistsGroup = all(existsInDF(val, uniqueVals) for val in spec.value)
					if spec.value and not checkValExistsGroup:
						printWarning = True


		if printWarning:
			#print warning
			raise ValueError("Input spec is inconsistent with DataFrame.")

		# lux.setContext(lux.Spec(attr = "Horsepower"))
		# lux.setContext(lux.Spec(attr = "A")) --> Warning

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
		for spec in ldf.context:
			specOptions = []
			if "attribute" in spec.type:
				if spec.attribute == "?":
					options = set(ldf.attrList)  # all attributes
					print(options)
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