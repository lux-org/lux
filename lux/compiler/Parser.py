from lux.context.Spec import Spec
from lux.luxDataFrame.LuxDataframe import LuxDataFrame
class Parser:
	"""
	The parser takes in the user's input context specification,
	then generates the Lux internal specification through lux.Spec.
	"""	
	@staticmethod
	def parse(ldf: LuxDataFrame) -> None:
		"""
		Given the string description from the input Spec,
		assign the appropriate spec.attribute, spec.filterOp, and spec.value.
		
		Parameters
		----------
		ldf : lux.luxDataFrame.LuxDataFrame
			LuxDataFrame with fully specified context consisting of lux.Spec objects.

		Returns
		-------
		None

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
					if type(v) is str and v in list(ldf.columns):
						validValues.append(v)
				tempSpec = Spec(attribute = validValues)
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
					if var in list(ldf.columns):
						tempSpec = Spec(attribute = var, filterOp = "=", value = validValues)
						newContext.append(tempSpec)
				#case where user specifies a variable
				else:
					if "|" in s:
						values = s.split("|")
						for v in values:
							if v in list(ldf.columns):
								validValues.append(v)
					else:
						validValues = s
					tempSpec = Spec(attribute = validValues)
					newContext.append(tempSpec)
			elif type(s) is Spec:
				newContext.append(s)
		parsedContext = newContext
		ldf.context = newContext

		for spec in parsedContext:
			if (spec.description):
				if ((spec.description in list(ldf.columns)) or spec.description == "?"):# if spec.description in the list of attributes
					spec.attribute = spec.description
				elif any(ext in [">","<","="] for ext in spec.description): # spec.description contain ">","<". or "="
					# then parse it and assign to spec.attribute, spec.filterOp, spec.values
					spec.filterOp = re.findall(r'/.*/>|=|<|>=|<=|!=', spec.description)[0]
					splitDescription = spec.description.split(spec.filterOp)
					spec.attribute = splitDescription[0]
					spec.value = splitDescription[1]
				elif (type(spec.description)==list):
					spec.attribute = spec.description
				else: # then it is probably a value 
					spec.values = spec.description

		ldf.context = parsedContext