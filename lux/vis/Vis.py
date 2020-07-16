from __future__ import annotations
from typing import List, Callable, Union
from lux.vis.VisSpec import VisSpec
from lux.utils.utils import check_import_lux_widget
class Vis:
	'''
	Vis Object represents a collection of fully fleshed out specifications required for data fetching and visualization.
	'''

	def __init__(self, spec_lst, source =None , mark="", title="", score=0.0):
		self.spec_lst = spec_lst
		self.source = source # This is the data that is attached to the Vis
		self.data = None # This is the data that represents the Vis (e.g., selected, aggregated, binned)
		self.title = title
		self.mark = mark
		self.score = score
		self.code = None
		self.plot_config = None
		self.x_min_max = {}
		self.y_min_max = {}
		if (source is not None): self.refresh_source(source)
	def __repr__(self):
		if self.source is None:
			return f"<Vis  ({str(self.spec_lst)}) mark: {self.mark}, score: {self.score} >"
		filter_spec = None
		channels, additional_channels = [], []
		for spec in self.spec_lst:

			if hasattr(spec,"value"):
				if spec.value != "":
					filter_spec = spec
			if hasattr(spec,"attribute"):
				if spec.attribute != "":
					if spec.aggregation != "":
						attribute = spec.aggregation.upper() + "(" + spec.attribute + ")"
					elif spec.bin_size > 0:
						attribute = "BIN(" + spec.attribute + ")"
					else:
						attribute = spec.attribute
					if spec.channel == "x":
						channels.insert(0, [spec.channel, attribute])
					elif spec.channel == "y":
						channels.insert(1, [spec.channel, attribute])
					elif spec.channel != "":
						additional_channels.append([spec.channel, attribute])

		channels.extend(additional_channels)
		str_channels = ""
		for channel in channels:
			str_channels += channel[0] + ": " + channel[1] + ", "

		if filter_spec:
			return f"<Vis  ({str_channels[:-2]} -- [{filter_spec.attribute}{filter_spec.filter_op}{filter_spec.value}]) mark: {self.mark}, score: {self.score} >"
		else:
			return f"<Vis  ({str_channels[:-2]}) mark: {self.mark}, score: {self.score} >"
	def get_specs(self) -> List[VisSpec]:
		"""
		Returns the VisSpecs describing the Vis 

		Returns
		-------
		List[VisSpec]
		"""		
		return self.spec_lst
	def set_specs(self, specs:List[VisSpec]) -> None:
		"""
		Sets the spec_lst of the Vis and refresh the source based on the new specs

		Parameters
		----------
		query : List[VisSpec]
			Query specifying the desired VisCollection
		"""		
		self.spec_lst = specs
		self.refresh_source(self.source)
	def set_plot_config(self,config_func:Callable):
		"""
		Modify plot aesthetic settings to the Vis
		Currently only supported for Altair visualizations

		Parameters
		----------
		config_func : typing.Callable
			A function that takes in an AltairChart (https://altair-viz.github.io/user_guide/generated/toplevel/altair.Chart.html) as input and returns an AltairChart as output
		"""
		self.plot_config = config_func
	def clear_plot_config(self):
		self.plot_config = None
	def _repr_html_(self):
		from IPython.display import display
		check_import_lux_widget()
		import luxWidget
		if (self.data is None):
			raise Exception("No data is populated in Vis. In order to generate data required for the vis, use the 'refresh_source' function to populate the Vis with a data source (e.g., vis.refresh_source(df)).")
		else:
			from lux.luxDataFrame.LuxDataframe import LuxDataFrame
			widget =  luxWidget.LuxWidget(
					currentView= LuxDataFrame.current_view_to_JSON([self]),
					recommendations=[],
					context={}
				)
			display(widget)
	def get_attr_by_attr_name(self,attr_name):
		return list(filter(lambda x: x.attribute == attr_name, self.spec_lst))
		
	def get_attr_by_channel(self, channel):
		spec_obj = list(filter(lambda x: x.channel == channel and x.value=='' if hasattr(x, "channel") else False, self.spec_lst))
		return spec_obj

	def get_attr_by_data_model(self, dmodel, exclude_record=False):
		if (exclude_record):
			return list(filter(lambda x: x.data_model == dmodel and x.value=='' if x.attribute!="Record" and hasattr(x, "data_model") else False, self.spec_lst))
		else:
			return list(filter(lambda x: x.data_model == dmodel and x.value=='' if hasattr(x, "data_model") else False, self.spec_lst))

	def get_attr_by_data_type(self, dtype):
		return list(filter(lambda x: x.data_type == dtype and x.value=='' if hasattr(x, "data_type") else False, self.spec_lst))

	def remove_filter_from_spec(self, value):
		self.spec_lst = list(filter(lambda x: x.value != value, self.spec_lst))

	def remove_column_from_spec(self, attribute, remove_first:bool=False):
		"""
		Removes an attribute from the Vis's spec

		Parameters
		----------
		attribute : str
			attribute to be removed
		remove_first : bool, optional
			Boolean flag to determine whether to remove all instances of the attribute or only one (first) instance, by default False
		"""		
		if (not remove_first):
			self.spec_lst = list(filter(lambda x: x.attribute != attribute, self.spec_lst))
		elif (remove_first):
			new_spec = []
			skip_check = False
			for i in range(0, len(self.spec_lst)):
				if self.spec_lst[i].value=="": # spec is type attribute
					column_spec = []
					column_names = self.spec_lst[i].attribute
					# if only one variable in a column, columnName results in a string and not a list so
					# you need to differentiate the cases
					if isinstance(column_names, list):
						for column in column_names:
							if (column != attribute) or skip_check:
								column_spec.append(column)
							elif (remove_first):
								remove_first = True
						new_spec.append(VisSpec(column_spec))
					else:
						if (column_names != attribute) or skip_check:
							new_spec.append(VisSpec(attribute = column_names))

						elif (remove_first):
							remove_first = True
					if (remove_first):
						skip_check = True
				else:
					new_spec.append(self.spec_lst[i])
			self.spec_lst = new_spec

	def to_Altair(self) -> str:
		"""
		Generate minimal Altair code to visualize the Vis

		Returns
		-------
		str
			String version of the Altair code. Need to print out the string to apply formatting.
		"""		
		from lux.vizLib.altair.AltairRenderer import AltairRenderer
		renderer = AltairRenderer(output_type="Altair")
		self.code= renderer.create_vis(self)
		return self.code

	def to_VegaLite(self, prettyOutput = True) -> Union[dict,str]:
		"""
		Generate minimal Vega-Lite code to visualize the Vis

		Returns
		-------
		Union[dict,str]
			String or Dictionary of the VegaLite JSON specification
		"""		
		import json
		from lux.vizLib.altair.AltairRenderer import AltairRenderer
		renderer = AltairRenderer(output_type="VegaLite")
		self.code = renderer.create_vis(self)
		if (prettyOutput):
			return "** Copy Text Below to Vega Editor(vega.github.io/editor) to Vis and edit **\n"+json.dumps(self.code, indent=2)
		else:
			return self.code
		
	def render_VSpec(self, renderer="altair"):
		if (renderer == "altair"):
			return self.to_VegaLite(prettyOutput=False)
	
	def refresh_source(self, ldf):# -> Vis:
		"""
		Loading the source data into the Vis by instantiating the specification and populating the Vis based on the source data, effectively "materializing" the Vis.

		Parameters
		----------
		ldf : LuxDataframe
			Input Dataframe to be attached to the Vis

		Returns
		-------
		Vis
			Complete Vis with fully-specified fields

		See Also
		--------
		lux.Vis.VisCollection.refresh_source
		"""		
		from lux.compiler.Parser import Parser
		from lux.compiler.Validator import Validator
		from lux.compiler.Compiler import Compiler
		from lux.executor.PandasExecutor import PandasExecutor #TODO: temporary (generalize to executor)
		self.source = ldf
		#TODO: handle case when user input vanilla Pandas dataframe
		self.spec_lst = Parser.parse(self.spec_lst)
		Validator.validate_spec(self.spec_lst,ldf)
		vc = Compiler.compile(ldf,ldf.context,[self],enumerate_collection=False)
		PandasExecutor.execute(vc,ldf)
		# Copying properties over since we can not redefine `self` within class function
		vis = vc[0]
		self.title = vis.title
		self.mark = vis.mark
		self.spec_lst = vis.spec_lst
		self.data = vis.data
		self.x_min_max = vis.x_min_max
		self.y_min_max = vis.y_min_max