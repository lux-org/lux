class Spec:
	'''
	Spec is the object representation of a single unit of the specification.
	'''
<<<<<<< HEAD
	def __init__(self, description="",attribute="",value="", axis="",
				filterOp="",attributeGroup=[],valueGroup=[], channel="",
				dataType="",dataModel="",aggregation = "", binning="", weight=""):
		# Descriptor
		self.description = description
		# Description gets comiled to either an attribute, value, attributeGroup or valueGroup
		self.attribute = attribute
		self.value = value
		self.axis = axis
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
			   f"attribute:{str(self.attribute)},"+ \
			   f"value:{str(self.value)}>"
		return repr

