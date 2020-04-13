import typing
class Spec:
	'''
	Spec is the object representation of a single unit of the specification.
	'''
	def __init__(self, description:str ="",attribute: typing.Union[str,list] ="",value: typing.Union[str,list]="",
				 filterOp:str ="", channel:str ="", dataType:str="",dataModel:str="",
				 aggregation:str = "", binSize:int=0, weight:float=1, type:str = ""):
		# Descriptor
		self.description = description
		# Description gets compiled to attribute, value, filterOp
		self.attribute = attribute
		self.value = value
		self.filterOp = filterOp
		# self.parseDescription()
		# Properties
		self.channel = channel
		self.dataType = dataType
		self.dataModel = dataModel
		self.aggregation = aggregation
		self.binSize = binSize
		self.weight = weight
			
	def __repr__(self):
		repr =  f"Spec < description:{str(self.description)},"+ \
			   f"channel:{str(self.channel)},"+ \
			   f"attribute:{str(self.attribute)},"+ \
			   f"aggregation:{str(self.aggregation)},"+ \
			   f"value:{str(self.value)}>" + \
			   f"dataModel:{str(self.dataModel)}," + \
				f"dataType:{str(self.dataType)},"+\
				f"binSize:{str(self.binSize)}"
		return repr

