# from ..luxDataFrame.LuxDataframe import LuxDataFrame
from lux.luxDataFrame.LuxDataframe import LuxDataFrame
from lux.vis.Clause import Clause
from typing import List
class Validator:
	'''
	Contains methods for validating lux.Clause objects in the intent.
	'''
	def __init__(self):
		self.name = "Validator"

	def __repr__(self):
		return f"<Validator>"

	@staticmethod
	def validate_intent(intent: List[Clause], ldf:LuxDataFrame) -> None:
		"""
		Validates input specifications from the user to find inconsistencies and errors.

		Parameters
		----------
		ldf : lux.luxDataFrame.LuxDataFrame
			LuxDataFrame with underspecified intent.

		Returns
		-------
		None

		Raises
		------
		ValueError
			Ensures no input intent are consistent with DataFrame.
		"""

		def validate_clause(clause):
			if not((clause.attribute and clause.attribute == "?") or (clause.value and clause.value=="?")):
				if isinstance(clause.attribute,list):
					for attr in clause.attribute:
						if attr not in list(ldf.columns):
							raise ValueError(f"The input attribute {attr} does not exist in the DataFrame.")
				else:
					if (clause.attribute and clause.attribute!="Record"):
						if not clause.attribute in list(ldf.columns):
							raise ValueError(f"The input attribute {clause.attribute} does not exist in the DataFrame.")
					if (clause.value and clause.attribute and clause.filter_op=="="):
						series = ldf[clause.attribute].values
						if isinstance(clause.value, list):
							vals = clause.value
						else:
							vals = [clause.value]
						for val in vals:
							if (val not in series):#(not series.str.contains(val).any()):
								raise ValueError(f"The input value {val} does not exist for the attribute {clause.attribute} for the DataFrame.")

		for clause in intent:
			if type(clause) is list:
				for s in clause:
					validate_clause(s)
			else:
				validate_clause(clause)