class Event():
	"""
	Event represents a single operation applied to the dataframe, with input arguments of operation recorded
	"""
	def __init__(self,name,*args,**kwargs):
		self.name = name
		self.args = args
		self.kwargs = kwargs
	def __repr__(self):
		if (self.args==() and self.kwargs=={}):
			return f"<Event: {self.name}>"
		else:
			return f"<Event: {self.name} -- args={self.args}, kwargs={self.kwargs}>"