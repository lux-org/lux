from __future__ import annotations
from typing import List, Callable, Union
from lux.context.Spec import Spec
from lux.utils.utils import check_import_lux_widget
class View:
	'''
	View Object represents a collection of fully fleshed out specifications required for data fetching and visualization.
	'''

	def __init__(self, spec_lst, mark="", title=""):
		self.spec_lst = spec_lst
		self.title = title
		self.mark = mark
		self.data = None
		self.score = 0.0
		self.vis = None
		self.plot_config = None
		self.x_min_max = {}
		self.y_min_max = {}
	def __repr__(self):
		if self.data is None:
			return f"<View  ({str(self.spec_lst)}) mark: {self.mark}, score: {self.score} >"
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
			return f"<View  ({str_channels[:-2]} -- [{filter_spec.attribute}{filter_spec.filter_op}{filter_spec.value}]) mark: {self.mark}, score: {self.score} >"
		else:
			return f"<View  ({str_channels[:-2]}) mark: {self.mark}, score: {self.score} >"
	def set_plot_config(self,config_func:Callable):
		"""
		Modify plot aesthetic settings to the View
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
			raise Exception("No data populated in View. Use the 'load' function (e.g., view.load(df)) to populate the view with a data source.")
		else:
			from lux.luxDataFrame.LuxDataframe import LuxDataFrame
			# widget  = LuxDataFrame.render_widget(input_current_view=self,render_target="viewOnly")
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

	def remove_column_from_spec(self, attribute):
		self.spec = list(filter(lambda x: x.attribute != attribute, self.spec_lst))

	def remove_column_from_spec_new(self, attribute:str,remove_first:bool=False):
		"""
		Removes an attribute from the View's spec

		Parameters
		----------
		attribute : str
			attribute to be removed
		remove_first : bool, optional
			Boolean flag to determine whether to remove all instances of the attribute or only one (first) instance, by default False
		"""		
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
					new_spec.append(Spec(column_spec))
				else:
					if (column_names != attribute) or skip_check:
						new_spec.append(Spec(attribute = column_names))
					elif (remove_first):
						remove_first = True
				if (remove_first):
					skip_check = True
			else:
				new_spec.append(self.spec_lst[i])
		self.spec_lst = new_spec
	def to_Altair(self) -> str:
		"""
		Generate minimal Altair code to visualize the view

		Returns
		-------
		str
			String version of the Altair code. Need to print out the string to apply formatting.
		"""		
		from lux.vizLib.altair.AltairRenderer import AltairRenderer
		renderer = AltairRenderer(output_type="Altair")
		self.vis= renderer.create_vis(self)
		return self.vis

	def to_VegaLite(self, prettyOutput = True) -> Union[dict,str]:
		"""
		Generate minimal Vega-Lite code to visualize the view

		Returns
		-------
		Union[dict,str]
			String or Dictionary of the VegaLite JSON specification
		"""		
		import json
		from lux.vizLib.altair.AltairRenderer import AltairRenderer
		renderer = AltairRenderer(output_type="VegaLite")
		self.vis = renderer.create_vis(self)
		if (prettyOutput):
			return "** Copy Text Below to Vega Editor(vega.github.io/editor) to view and edit **\n"+json.dumps(self.vis, indent=2)
		else:
			return self.vis
		
	def render_VSpec(self, renderer="altair"):
		if (renderer == "altair"):
			return self.to_VegaLite(prettyOutput=False)
	
	def load(self, ldf) -> View:
		"""
		Loading the data into the view by instantiating the specification and populating the view based on the data, effectively "materializing" the view.

		Parameters
		----------
		ldf : LuxDataframe
			Input Dataframe to be attached to the view

		Returns
		-------
		View
			Complete View with fully-specified fields

		See Also
		--------
		lux.view.ViewCollection.load
		"""		
		from lux.compiler.Parser import Parser
		from lux.compiler.Validator import Validator
		from lux.compiler.Compiler import Compiler
		from lux.executor.PandasExecutor import PandasExecutor #TODO: temporary (generalize to executor)
		#TODO: handle case when user input vanilla Pandas dataframe
		self.spec_lst = Parser.parse(self.spec_lst)
		Validator.validate_spec(self.spec_lst,ldf)
		vc = Compiler.compile(ldf,ldf.context,[self],enumerate_collection=False)
		PandasExecutor.execute(vc,ldf)
		return vc[0]