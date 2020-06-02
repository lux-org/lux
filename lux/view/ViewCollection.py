from lux.vizLib.altair.AltairRenderer import AltairRenderer
from lux.utils.utils import checkImportLuxWidget
class ViewCollection():
	'''
	ViewCollection is a list of View objects. 
	'''
	def __init__(self,collection):
		self.collection=collection

	def __getitem__(self, key):
		return self.collection[key]
	def __setitem__(self, key, value):
		self.collection[key] = value
	def __len__(self):
		return len(self.collection)
	def __repr__(self):
		x_channel = ""
		y_channel = ""
		largest_mark = 0
		largest_filter = 0
		for view in self.collection: #finds longest x attribute among all views
			filter_spec = None
			for spec in view.specLst:
				if spec.value != "":
					filter_spec = spec
				if spec.channel == "x" and len(x_channel) < len(spec.attribute):
					x_channel = spec.attribute
				if spec.channel == "y" and len(y_channel) < len(spec.attribute):
					y_channel = spec.attribute
			if len(view.mark) > largest_mark:
				largest_mark = len(view.mark)
			if filter_spec and len(str(filter_spec.value)) + len(filter_spec.attribute) > largest_filter:
				largest_filter = len(str(filter_spec.value)) + len(filter_spec.attribute) 
		views_repr = []
		largest_x_length = len(x_channel)
		largest_y_length = len(y_channel)
		for view in self.collection: #pads the shorter views with spaces before the y attribute
			filter_spec = None
			x_channel = ""
			y_channel = ""
			for spec in view.specLst:
				if spec.value != "":
					filter_spec = spec
				if spec.channel == "x":
					x_channel = spec.attribute.ljust(largest_x_length)
				elif spec.channel == "y":
					y_channel = spec.attribute
			if filter_spec:
				y_channel = y_channel.ljust(largest_y_length)
			elif largest_filter != 0:
				y_channel = y_channel.ljust(largest_y_length + largest_filter + 9)
			else:
				y_channel = y_channel.ljust(largest_y_length + largest_filter)
			aligned_mark = view.mark.ljust(largest_mark)
			if filter_spec:
				aligned_filter = " -- [" + filter_spec.attribute + filter_spec.filterOp + str(filter_spec.value) + "]"
				aligned_filter = aligned_filter.ljust(largest_filter + 8)
				views_repr.append(f" <View  (x: {x_channel}, y: {y_channel} {aligned_filter}) mark: {aligned_mark}, score: {view.score:.2f} >") 
			else:
				views_repr.append(f" <View  (x: {x_channel}, y: {y_channel}) mark: {aligned_mark}, score: {view.score:.2f} >") 
		return '['+',\n'.join(views_repr)[1:]+']'
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
		return ViewCollection(self.collection[:k])
	def bottomK(self,k):
		#sort and truncate list to first K items
		self.sort(descending=False)
		return ViewCollection(self.collection[:k])
	def normalizeScore(self, invertOrder = False):
		maxScore = max(list(self.get("score")))
		for dobj in self.collection:
			dobj.score = dobj.score/maxScore
			if (invertOrder): dobj.score = 1 - dobj.score
	def _repr_html_(self):
		from IPython.display import display
		from lux.luxDataFrame.LuxDataframe import LuxDataFrame
		# widget  = LuxDataFrame.renderWidget(inputCurrentView=self,renderTarget="viewCollectionOnly")
		recommendation = {"action": "View Collection",
					  "description": "Shows a view collection defined by the context"}
		recommendation["collection"] = self

		checkImportLuxWidget()
		import luxWidget
		recJSON = LuxDataFrame.recToJSON([recommendation])
		widget =  luxWidget.LuxWidget(
				currentView={},
				recommendations=recJSON,
				context={}
			)
		display(widget)	