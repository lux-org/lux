import typing
class VisSpec:
	def __init__(self, description:typing.Union[str,list] ="",attribute: typing.Union[str,list] ="",value: typing.Union[str,list]="",
				 filter_op:str ="=", channel:str ="", data_type:str="",data_model:str="",
				 aggregation:str = "", bin_size:int=0, weight:float=1,sort:str="", exclude: typing.Union[str,list] =""):
		"""
		VisSpec is the object representation of a single unit of the specification.

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
		aggregation : str, optional
			Aggregation function for specified attribute, by default ""
			Possible values: 'sum','mean', and others supported by Pandas.aggregate (https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.aggregate.html), including numpy aggregation functions (e.g., np.ptp), by default ""
		bin_size : int, optional
			Number of bins for histograms, by default 0
		weight : float, optional
			A number between 0 and 1 indicating the importance of this VisSpec, by default 1
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
		self.aggregation = aggregation
		self.bin_size = bin_size
		self.weight = weight
		self.sort = sort
		self.exclude = exclude

		# If aggregation input is a function (e.g., np.std), get the string name of the function for plotting
		if hasattr(self.aggregation,'__name__'): 
			self._aggregation_name = self.aggregation.__name__
		else:
			self._aggregation_name = self.aggregation

	def copy_spec(self):
		description_copy = self.description
		# Description gets compiled to attribute, value, filter_op
		attribute_copy = self.attribute
		value_copy = self.value
		filter_op_copy = self.filter_op
		# self.parseDescription()
		# Properties
		channel_copy = self.channel
		data_type_copy = self.data_type
		data_model_copy = self.data_model
		aggregation_copy = self.aggregation
		bin_size_copy = self.bin_size
		weight_copy = self.weight
		sort_copy = self.sort
		exclude_copy = self.exclude

		copied_spec = VisSpec(description = description_copy, attribute = attribute_copy, value = value_copy, filter_op = filter_op_copy, channel = channel_copy, data_type = data_type_copy, data_model = data_model_copy, aggregation = aggregation_copy, bin_size = bin_size_copy, weight = weight_copy, sort = sort_copy, exclude = exclude_copy)
		return copied_spec

	def __repr__(self):
		attributes = []
		if self.description != "":
			attributes.append("         description: " + self.description)
		if self.channel != "":
			attributes.append("         channel: " + self.channel)
		if len(self.attribute) != 0:
			attributes.append("         attribute: " + str(self.attribute))
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
		attributes[0] = "<VisSpec" + attributes[0][5:]
		attributes[len(attributes) - 1] += " >"
		return ',\n'.join(attributes)
