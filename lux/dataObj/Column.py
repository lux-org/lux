class Column:
	'''
	Column Object represents one or a group of datapoints (columns) in the Dataset.
	'''
	def __init__(self, columnName, channel="", dataType="",dataModel="", transform="",aggregation="",binning="",scale=""):
		self.className = "Column"
		# Descriptor
		self.columnName = columnName
		# Properties
		self.channel = channel
		self.dataType = dataType
		self.dataModel = dataModel
		self.transform = transform
		self.aggregation = aggregation
		self.binning = binning
		self.scale = scale
	def __repr__(self):
		repr =  f"Column <{str(self.columnName)},"+ \
			   f"channel:{str(self.channel)},"+ \
			   f"dataType:{str(self.dataType)},"+ \
			   f"dataModel:{str(self.dataModel)}>"
		return repr

