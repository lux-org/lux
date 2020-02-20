class Spec:
    '''
    Spec is the object representation of a single unit of the specification.
    '''
    def __init__(self, 
                description, 
                channel="", 
                dataType="",
                dataModel="", 
                transform="",
                aggregation="",
                binning="",
                exclude=False):
		# Descriptor
		self.description = description
        # Description gets comiled to either an attribute, value, attributeGroup or valueGroup
        # self.attribute = ""
        # self.value = ""
        # self.filterOp = ""
        # self.attributeGroup = []
        # self.valueGroup = []
        # self.type = "Attribute", "Filter", "Group"
        # self.parseDescription()
		# Properties
		self.channel = channel
		self.dataType = dataType
		self.dataModel = dataModel
		self.transform = transform
		self.aggregation = aggregation
		self.binning = binning
        self.exclude = exclude
	# def parseDescription():
    #     # Description gets compiled to either an attribute, value, attributeGroup or valueGroup
    #     if type(description)==list:
    #         # set the self.type as "Group"
    #         # check if this is an attribute
    #         # if so set it as self.attributeGroup 
    #     elif type(description)==str:
    #         # Check if this is an attribute
    #         # if so set the self.type as "Attribute"
    #         # Otherwise check if this is a value
    #         # if so set the self.type as "Value"

            
	def __repr__(self):
		repr =  f"Spec <{str(self.columnName)},"+ \
			   f"channel:{str(self.channel)},"+ \
			   f"dataType:{str(self.dataType)},"+ \
			   f"dataModel:{str(self.dataModel)}>"
		return repr

