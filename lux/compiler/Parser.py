from lux.context.Spec import Spec
from lux.luxDataFrame.LuxDataframe import LuxDataFrame
from typing import List
class Parser:
	"""
	The parser takes in the user's input specifications (with string `description` fields),
	then generates the Lux internal specification through lux.Spec.
	"""	
	@staticmethod
	def parse(specs: List[Spec]) -> List[Spec]:
		"""
		Given the string description from a list of input Specs (often context),
		assign the appropriate spec.attribute, spec.filterOp, and spec.value.
		
		Parameters
		----------
		specs : List[Spec]
			Underspecified list of lux.Spec objects.

		Returns
		-------
		List[Spec]
			Parsed list of lux.Spec objects.
		"""		
		import re
		# specs = ldf.getContext()
		newContext = []
		#checks for and converts users' string inputs into lux specifications
		for s in specs:
			validValues = []
			if type(s) is list:
				validValues = []
				for v in s:
					if type(v) is str: # and v in list(ldf.columns): #TODO: Move validation check to Validator
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
							# if v in ldf.uniqueValues[var]: #TODO: Move validation check to Validator
							validValues.append(v)
					else:
						validValues = s[eqInd+1:]
					# if var in list(ldf.columns): #TODO: Move validation check to Validator
					tempSpec = Spec(attribute = var, filterOp = "=", value = validValues)
					newContext.append(tempSpec)
				#case where user specifies a variable
				else:
					if "|" in s:
						values = s.split("|")
						for v in values:
							# if v in list(ldf.columns): #TODO: Move validation check to Validator
							validValues.append(v)
					else:
						validValues = s
					tempSpec = Spec(attribute = validValues)
					newContext.append(tempSpec)
			elif type(s) is Spec:
				newContext.append(s)
		specs = newContext
		# ldf.context = newContext

		for spec in specs:
			if (spec.description):
				#TODO: Move validation check to Validator
				#if ((spec.description in list(ldf.columns)) or spec.description == "?"):# if spec.description in the list of attributes
				if any(ext in [">","<","="] for ext in spec.description): # spec.description contain ">","<". or "="
					# then parse it and assign to spec.attribute, spec.filterOp, spec.values
					spec.filterOp = re.findall(r'/.*/>|=|<|>=|<=|!=', spec.description)[0]
					splitDescription = spec.description.split(spec.filterOp)
					spec.attribute = splitDescription[0]
					spec.value = splitDescription[1]
				elif (type(spec.description) == str):
					spec.attribute = spec.description
				elif (type(spec.description)==list):
					spec.attribute = spec.description
				# else: # then it is probably a value 
				# 	spec.values = spec.description
		return specs
		# ldf.context = specs