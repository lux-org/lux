from lux.vizLib.altair.AltairRenderer import AltairRenderer

class DataObjCollection:
	'''
	DataObjCollection is a list of DataObjects. 
	'''
	def __init__(self,collection):
		self.collection=collection

	def __repr__(self):
		return f"<Data Obj Collection: {str(self.collection)}>"

	def map(self,function):
		# generalized way of applying a function to each element
		return map(function, self.collection)
	
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
		if (removeInvalid): self.collection = list(filter(lambda x: x.score!=-1,self.collection))
		# sort in-place by “score” by default if available, otherwise user-specified field to sort by
		self.collection.sort(key=lambda x: x.score, reverse=descending)

	def topK(self,k):
		#sort and truncate list to first K items
		self.sort()
		return DataObjCollection(self.collection[:k])
	def bottomK(self,k):
		#sort and truncate list to first K items
		self.sort(descending=False)
		return DataObjCollection(self.collection[:k])
	def normalizeScore(self, invertOrder = False):
		maxScore = max(list(self.get("score")))
		for dobj in self.collection:
			dobj.score = dobj.score/maxScore
			if (invertOrder): dobj.score = 1 - dobj.score 

	
