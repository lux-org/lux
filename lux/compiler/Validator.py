# from ..luxDataFrame.LuxDataframe import LuxDataFrame
from lux.luxDataFrame.LuxDataframe import LuxDataFrame
from lux.vis.VisSpec import VisSpec
from typing import List
class Validator:
	'''
	Contains methods for validating lux.VisSpec objects in the context.
	'''
	def __init__(self):
		self.name = "Validator"

	def __repr__(self):
		return f"<Validator>"

	@staticmethod
	def validate_spec(specs: List[VisSpec], ldf:LuxDataFrame) -> None:
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
			Ensures no input specs are consistent with DataFrame.
		"""
		unique_vals = ldf.unique_values
		print_warning = False

		def exists_in_df(value, unique_values):
			return any(value in unique_values[vals] for vals in unique_values)

		def validate_attr(spec):
			if not((spec.attribute and spec.attribute == "?") or (spec.value and spec.value=="?")):
				if isinstance(spec.attribute,list):
					check_attr_exists_group = all(attr in list(ldf.columns) for attr in spec.attribute)
					if spec.attribute and not check_attr_exists_group:
						print_warning = True
				else:
						check_attr_exists = spec.attribute in list(ldf.columns)
						if spec.attribute and not check_attr_exists:
							print_warning = True

						if isinstance(spec.value, list):
							check_val_exists = spec.attribute in unique_vals and all(v in unique_vals[spec.attribute] for v in spec.value)
						else:
							check_val_exists = spec.attribute in unique_vals and spec.value in unique_vals[spec.attribute]
						if spec.value and not check_val_exists:
							print_warning = True
				
				if isinstance(spec.value, list):
					check_val_exists_group = all(exists_in_df(val, unique_vals) for val in spec.value)
					if spec.value and not check_val_exists_group:
						print_warning = True

		# 1. Parse all string specification into VisSpec objects (nice-to-have)
		# 2. Validate that the parsed specification is corresponds to the content in the LuxDataframe.
		for spec in specs:
			if type(spec) is list:
				for s in spec:
					validate_attr(s)
			else:
				validate_attr(spec)

		if print_warning:
			raise ValueError("Input spec is inconsistent with DataFrame.")

		# lux.set_context(lux.VisSpec(attr = "Horsepower"))
		# lux.set_context(lux.VisSpec(attr = "A")) --> Warning
