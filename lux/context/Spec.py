import typing
class Spec:
	def __init__(self, description:typing.Union[str,list] ="",attribute: typing.Union[str,list] ="",value: typing.Union[str,list]="",
				 filterOp:str ="=", channel:str ="", dataType:str="",dataModel:str="",
				 aggregation:str = "", binSize:int=0, weight:float=1,sort:str="", exclude: typing.Union[str,list] =""):
		"""
		Spec is the object representation of a single unit of the specification.

		Parameters
		----------
		description : typing.Union[str,list], optional
			Convenient shorthand description of specification, parser parses description into other properties (attribute, value, filterOp), by default ""
		attribute : typing.Union[str,list], optional
			Specified attribute(s) of interest, by default ""
			By providing a list of attributes (e.g., [Origin,Brand]), user is interested in either one of the attribute (i.e., Origin or Brand).
		value : typing.Union[str,list], optional
			Specified value(s) of interest, by default ""
			By providing a list of values (e.g., ["USA","Europe"]), user is interested in either one of the attribute (i.e., USA or Europe).
		filterOp : str, optional
			Filter operation of interest.
			Possible values: '=', '<', '>', '<=', '>=', '!=', by default "="
		channel : str, optional
			Encoding channel where the specified attribute should be placed.
			Possible values: 'x','y','color', by default ""
		dataType : str, optional
			Data type for the specified attribute.
			Possible values: 'nominal', 'quantitative', 'ordinal','temporal', by default ""
		dataModel : str, optional
			Data model for the specified attribute
			Possible values: 'dimension', 'measure', by default ""
		aggregation : str, optional
			Aggregation function for specified attribute, by default ""
			Possible values: 'sum','mean', and others supported by Pandas.aggregate (https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.aggregate.html), by default ""
		binSize : int, optional
			Number of bins for histograms, by default 0
		weight : float, optional
			A number between 0 and 1 indicating the importance of this Spec, by default 1
		sort : str, optional
			Specifying whether and how the bar chart should be sorted
			Possible values: 'ascending', 'descending', by default ""
		"""		
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
		self.sort = sort
		self.exclude = exclude
			
	def __repr__(self):
		attributes = []
		if self.description != "":
			attributes.append("         description: " + self.description)
		if self.channel != "":
			attributes.append("         channel: " + self.channel)
		if len(self.attribute) != 0:
			attributes.append("         attribute: " + str(self.attribute))
		if self.aggregation != "":
			attributes.append("         aggregation: " + self.aggregation)
		if len(self.value) != 0:
			attributes.append("         value: " + str(self.value))
		if self.dataModel != "":
			attributes.append("         dataModel: " + self.dataModel)
		if len(self.dataType) != 0:
			attributes.append("         dataType: " + str(self.dataType))
		if self.binSize != None:
			attributes.append("         binSize: " + str(self.binSize))
		if len(self.exclude) != 0:
			attributes.append("         exclude: " + str(self.exclude))
		attributes[0] = "<Spec" + attributes[0][5:]
		attributes[len(attributes) - 1] += " >"
		return ',\n'.join(attributes)
