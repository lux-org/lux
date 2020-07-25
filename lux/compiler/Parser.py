from lux.vis.Clause import Clause
from lux.luxDataFrame.LuxDataframe import LuxDataFrame
from typing import List
class Parser:
	"""
	The parser takes in the user's input specifications (with string `description` fields),
	then generates the Lux internal specification through lux.Clause.
	"""	
	@staticmethod
	def parse(intent: List[Clause]) -> List[Clause]:
		"""
		Given the string description from a list of input Clauses (intent),
		assign the appropriate clause.attribute, clause.filter_op, and clause.value.
		
		Parameters
		----------
		intent : List[Clause]
			Underspecified list of lux.Clause objects.

		Returns
		-------
		List[Clause]
			Parsed list of lux.Clause objects.
		"""		
		import re
		# intent = ldf.get_context()
		new_context = []
		#checks for and converts users' string inputs into lux specifications
		for s in intent:
			valid_values = []
			if type(s) is list:
				valid_values = []
				for v in s:
					if type(v) is str: # and v in list(ldf.columns): #TODO: Move validation check to Validator
						valid_values.append(v)
				temp_spec = Clause(attribute = valid_values)
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
					temp_spec = Clause(attribute = var, filter_op = "=", value = valid_values)
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
					temp_spec = Clause(attribute = valid_values)
					new_context.append(temp_spec)
			elif type(s) is Clause:
				new_context.append(s)
		intent = new_context
		# ldf.intent = new_context

		for clause in intent:
			if (clause.description):
				#TODO: Move validation check to Validator
				#if ((clause.description in list(ldf.columns)) or clause.description == "?"):# if clause.description in the list of attributes
				if any(ext in [">","<","=","!="] for ext in clause.description): # clause.description contain ">","<". or "="
					# then parse it and assign to clause.attribute, clause.filter_op, clause.values
					clause.filter_op = re.findall(r'/.*/|>|=|<|>=|<=|!=', clause.description)[0]
					split_description = clause.description.split(clause.filter_op)
					clause.attribute = split_description[0]
					clause.value = split_description[1]
					if re.match(r'^-?\d+(?:\.\d+)?$', clause.value):
						clause.value = float(clause.value)
				elif (type(clause.description) == str):
					clause.attribute = clause.description
				elif (type(clause.description)==list):
					clause.attribute = clause.description
				# else: # then it is probably a value 
				# 	clause.values = clause.description
		return intent
		# ldf.intent = intent