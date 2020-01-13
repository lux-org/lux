class Row:
	'''
	Row Object represents one or a group of datapoints (rows) in the Dataset.
	'''
	def __init__(self, fAttribute="", fVal= "",fOp = "=", function = "filter"):
		self.className = "Row"
		# Constraint-based specification (e.g., Origin = USA) #TODO: need to extend this with logical operators
		self.fAttribute = fAttribute
		self.fVal = fVal
		self.fOp = fOp
		# TODO: extend to rowID based specification
		self.points = []
		# Properties
		self.function = function # Row object can serve as different functions, it can be a filter, or highlight, or can be labelled as clusters or outliers.
		
	def __repr__(self):
		return f"Row <{str(self.fAttribute)},{str(self.fVal)}>"

