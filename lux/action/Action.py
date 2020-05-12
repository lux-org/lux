class Action:
	'''
	Abstract class for an action, where an action is an analytical module for computing visual recommendations.
	'''
	def __init__(self):
		self.name = ""
		self.description = ""
		self.dobj_requirement = {}
	def __repr__(self):
		return f"<Action: {str(self.settings)}>"
			
	def check_requirement(dobj):
		# Check whether data object has the right set of requirements to execute this action
		raise NotImplementedError

	def compute(dobj):
		# Enumerate --> compute the scores for each item in the collection 
		# -->  return DataObjectCollection with the scores 
		raise NotImplementedError

	def displayAsWidget():
		# display result in widget
		raise NotImplementedError

