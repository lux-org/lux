from lux.vizLib.altair.AltairRenderer import AltairRenderer

class ViewCollection():
	'''
	ViewCollection is a list of View objects. 
	'''
	def __init__(self,collection):
		self._collection=collection

	def __getitem__(self, key):
		return self._collection[key]
	def __setitem__(self, key, value):
		self._collection[key] = value
	def __len__(self):
		return len(self._collection)
	def __repr__(self):
		return f"<ViewCollection: {str(self._collection)}>"

	def map(self,function):
		# generalized way of applying a function to each element
		return map(function, self._collection)
	
	def get(self,fieldName):
		# Get the value of the field for all objects in the collection
		def getField(dObj):
			fieldVal = getattr(dObj,fieldName)
			# Might want to write catch error if key not in field
			return fieldVal
		return self.map(getField)

	def set(self,fieldName,fieldVal):
		return NotImplemented

	def sort(self, removeInvalid=True, descending = True):
		# remove the items that have invalid (-1) score
		if (removeInvalid): self._collection = list(filter(lambda x: x.score!=-1,self._collection))
		# sort in-place by “score” by default if available, otherwise user-specified field to sort by
		self._collection.sort(key=lambda x: x.score, reverse=descending)

	def topK(self,k):
		#sort and truncate list to first K items
		self.sort()
		return ViewCollection(self._collection[:k])
	def bottomK(self,k):
		#sort and truncate list to first K items
		self.sort(descending=False)
		return ViewCollection(self._collection[:k])
	def normalizeScore(self, invertOrder = False):
		maxScore = max(list(self.get("score")))
		for dobj in self._collection:
			dobj.score = dobj.score/maxScore
			if (invertOrder): dobj.score = 1 - dobj.score 
	
	
