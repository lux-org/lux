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
		assign the appropriate spec.attribute, spec.filter_op, and spec.value.
		
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
		# specs = ldf.get_context()
		new_context = []
		#checks for and converts users' string inputs into lux specifications
		for s in specs:
			valid_values = []
			if type(s) is list:
				valid_values = []
				for v in s:
					if type(v) is str: # and v in list(ldf.columns): #TODO: Move validation check to Validator
						valid_values.append(v)
				temp_spec = Spec(attribute = valid_values)
				new_context.append(temp_spec)
			elif type(s) is str:
				#case where user specifies a filter
				if "=" in s:
					eqInd = s.index("=")
					var = s[0:eqInd]
					if "|" in s:
						values = s[eqInd+1:].split("|")
						for v in values:
							# if v in ldf.unique_values[var]: #TODO: Move validation check to Validator
							valid_values.append(v)
					else:
						valid_values = s[eqInd+1:]
					# if var in list(ldf.columns): #TODO: Move validation check to Validator
					temp_spec = Spec(attribute = var, filter_op = "=", value = valid_values)
					new_context.append(temp_spec)
				#case where user specifies a variable
				else:
					if "|" in s:
						values = s.split("|")
						for v in values:
							# if v in list(ldf.columns): #TODO: Move validation check to Validator
							valid_values.append(v)
					else:
						valid_values = s
					temp_spec = Spec(attribute = valid_values)
					new_context.append(temp_spec)
			elif type(s) is Spec:
				new_context.append(s)
		specs = new_context
		# ldf.context = new_context

		for spec in specs:
			if (spec.description):
				#TODO: Move validation check to Validator
				#if ((spec.description in list(ldf.columns)) or spec.description == "?"):# if spec.description in the list of attributes
				if any(ext in [">","<","=","!="] for ext in spec.description): # spec.description contain ">","<". or "="
					# then parse it and assign to spec.attribute, spec.filter_op, spec.values
					spec.filter_op = re.findall(r'/.*/|>|=|<|>=|<=|!=', spec.description)[0]
					split_description = spec.description.split(spec.filter_op)
					spec.attribute = split_description[0]
					spec.value = split_description[1]
					if re.match(r'^-?\d+(?:\.\d+)?$', spec.value):
						spec.value = float(spec.value)
				elif (type(spec.description) == str):
					spec.attribute = spec.description
				elif (type(spec.description)==list):
					spec.attribute = spec.description
				# else: # then it is probably a value 
				# 	spec.values = spec.description
		return specs
		# ldf.context = specs