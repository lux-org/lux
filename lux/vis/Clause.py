import typing
class Clause:
	def __init__(self, description:typing.Union[str,list] ="",attribute: typing.Union[str,list] ="",value: typing.Union[str,list]="",
				 filter_op:str ="=", channel:str ="", data_type:str="",data_model:str="",
				 aggregation:typing.Union[str,callable] = "", bin_size:int=0, weight:float=1,sort:str="", exclude: typing.Union[str,list] =""):
		"""
		Clause is the object representation of a single unit of the specification.

		Parameters
		----------
		description : typing.Union[str,list], optional
			Convenient shorthand description of specification, parser parses description into other properties (attribute, value, filter_op), by default ""
		attribute : typing.Union[str,list], optional
			Specified attribute(s) of interest, by default ""
			By providing a list of attributes (e.g., [Origin,Brand]), user is interested in either one of the attribute (i.e., Origin or Brand).
		value : typing.Union[str,list], optional
			Specified value(s) of interest, by default ""
			By providing a list of values (e.g., ["USA","Europe"]), user is interested in either one of the attribute (i.e., USA or Europe).
		filter_op : str, optional
			Filter operation of interest.
			Possible values: '=', '<', '>', '<=', '>=', '!=', by default "="
		channel : str, optional
			Encoding channel where the specified attribute should be placed.
			Possible values: 'x','y','color', by default ""
		data_type : str, optional
			Data type for the specified attribute.
			Possible values: 'nominal', 'quantitative', 'ordinal','temporal', by default ""
		data_model : str, optional
			Data model for the specified attribute
			Possible values: 'dimension', 'measure', by default ""
		aggregation : typing.Union[str,callable], optional
			Aggregation function for specified attribute, by default ""
			Possible values: 'sum','mean', and others string shorthand or functions supported by Pandas.aggregate (https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.aggregate.html), including numpy aggregation functions (e.g., np.ptp), by default ""
		bin_size : int, optional
			Number of bins for histograms, by default 0
		weight : float, optional
			A number between 0 and 1 indicating the importance of this Clause, by default 1
		sort : str, optional
			Specifying whether and how the bar chart should be sorted
			Possible values: 'ascending', 'descending', by default ""
		"""		
		# Descriptor
		self.description = description
		# Description gets compiled to attribute, value, filter_op
		self.attribute = attribute
		self.value = value
		self.filter_op = filter_op
		# self.parseDescription()
		# Properties
		self.channel = channel
		self.data_type = data_type
		self.data_model = data_model
		self.set_aggregation(aggregation)
		self.bin_size = bin_size
		self.weight = weight
		self.sort = sort
		self.exclude = exclude
		
	def set_aggregation(self,aggregation:typing.Union[str,callable]):
		"""
		Sets the aggregation function of Clause, 
		while updating _aggregation_name internally

		Parameters
		----------
		aggregation : typing.Union[str,callable]
		"""		
		self.aggregation = aggregation
		# If aggregation input is a function (e.g., np.std), get the string name of the function for plotting
		if hasattr(self.aggregation,'__name__'): 
			self._aggregation_name = self.aggregation.__name__
		else:
			self._aggregation_name = self.aggregation
	def __repr__(self):
		attributes = []
		if self.description != "":
			attributes.append("         description: " + self.description)
		if self.channel != "":
			attributes.append("         channel: " + self.channel)
		if len(self.attribute) != 0:
			attributes.append("         attribute: " + str(self.attribute))
		if self.filter_op != "=":
			attributes.append(f"         filter_op: {str(self.filter_op)}" )
		if self.aggregation != "":
			attributes.append("         aggregation: " + self._aggregation_name)
		if self.value!="" or  len(self.value) != 0 :
			attributes.append("         value: " + str(self.value))
		if self.data_model != "":
			attributes.append("         data_model: " + self.data_model)
		if len(self.data_type) != 0:
			attributes.append("         data_type: " + str(self.data_type))
		if self.bin_size != None:
			attributes.append("         bin_size: " + str(self.bin_size))
		if len(self.exclude) != 0:
			attributes.append("         exclude: " + str(self.exclude))
		attributes[0] = "<Clause" + attributes[0][7:]
		attributes[len(attributes) - 1] += " >"
		return ',\n'.join(attributes)