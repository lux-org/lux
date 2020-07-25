# from ..luxDataFrame.LuxDataframe import LuxDataFrame
from lux.luxDataFrame.LuxDataframe import LuxDataFrame
from lux.vis.Clause import Clause
from typing import List
class Validator:
	'''
	Contains methods for validating lux.Clause objects in the context.
	'''
	def __init__(self):
		self.name = "Validator"

	def __repr__(self):
		return f"<Validator>"

	@staticmethod
	def validate_spec(intent: List[Clause], ldf:LuxDataFrame) -> None:
		"""
		Validates input specifications from the user to find inconsistencies and errors.

		Parameters
		----------
		ldf : lux.luxDataFrame.LuxDataFrame
			LuxDataFrame with underspecified context.

		Returns
		-------
		None

		Raises
		------
		ValueError
			Ensures no input intent are consistent with DataFrame.
		"""
		unique_vals = ldf.unique_values
		print_warning = False

		def exists_in_df(value, unique_values):
			return any(value in unique_values[vals] for vals in unique_values)

		def validate_attr(clause):
			if not((clause.attribute and clause.attribute == "?") or (clause.value and clause.value=="?")):
				if isinstance(clause.attribute,list):
					check_attr_exists_group = all(attr in list(ldf.columns) for attr in clause.attribute)
					if clause.attribute and not check_attr_exists_group:
						print_warning = True
				else:
						check_attr_exists = clause.attribute in list(ldf.columns)
						if clause.attribute and not check_attr_exists:
							print_warning = True

						if isinstance(clause.value, list):
							check_val_exists = clause.attribute in unique_vals and all(v in unique_vals[clause.attribute] for v in clause.value)
						else:
							check_val_exists = clause.attribute in unique_vals and clause.value in unique_vals[clause.attribute]
						if clause.value and not check_val_exists:
							print_warning = True
				
				if isinstance(clause.value, list):
					check_val_exists_group = all(exists_in_df(val, unique_vals) for val in clause.value)
					if clause.value and not check_val_exists_group:
						print_warning = True

		# 1. Parse all string specification into Clause objects (nice-to-have)
		# 2. Validate that the parsed specification is corresponds to the content in the LuxDataframe.
		for clause in intent:
			if type(clause) is list:
				for s in clause:
					validate_attr(s)
			else:
				validate_attr(clause)

		if print_warning:
			raise ValueError("Input clause is inconsistent with DataFrame.")

		# lux.set_intent(lux.Clause(attr = "Horsepower"))
		# lux.set_intent(lux.Clause(attr = "A")) --> Warning
