class Spec:
	'''
	Spec is the object representation of a single unit of the specification.
	'''
	def __init__(self, description="",attribute="",value="", filterOp="", channel="",
				 dataType="",dataModel="",aggregation = "", binning="", weight=""):
		# Descriptor
		self.description = description
		# Description gets comiled to either an attribute, value, attributeGroup or valueGroup
		self.attribute = attribute
		self.value = value
		self.filterOp = filterOp
		# self.attributeGroup = attributeGroup
		# self.valueGroup = valueGroup
		self.type = "" # automatically generated in validateSpec: ["attribute", "value", "attributeGroup", "valueGroup"]
		# self.parseDescription()
		# Properties
		self.channel = channel
		self.dataType = dataType
		self.dataModel = dataModel
		self.aggregation = aggregation
		self.binning = binning
		self.weight = weight
			
	def __repr__(self):
		repr =  f"Spec < description:{str(self.description)},"+ \
			   f"channel:{str(self.channel)},"+ \
			   f"attribute:{str(self.attribute)},"+ \
			   f"value:{str(self.value)}>" + \
			   f"dataModel:{str(self.dataModel)}," + \
				f"dataType:{str(self.dataType)}"
		return repr

