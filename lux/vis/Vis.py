from __future__ import annotations
from typing import List, Callable, Union
from lux.vis.Clause import Clause
from lux.utils.utils import check_import_lux_widget
class Vis:
	'''
	Vis Object represents a collection of fully fleshed out specifications required for data fetching and visualization.
	'''

	def __init__(self, intent, source =None , mark="", title="", score=0.0):
		self.intent = intent # This is the user's original intent to Vis
		self._inferred_intent = intent # This is the re-written, expanded version of user's original intent (include inferred vis info)
		self.source = source # This is the original data that is attached to the Vis
		self.data = None # This is the data that represents the Vis (e.g., selected, aggregated, binned)
		self.title = title
		self.mark = mark
		self.score = score
		self.code = None
		self.plot_config = None
		self.min_max = {}
		if (source is not None): self.refresh_source(source)
	def __repr__(self):
		if self.source is None:
			return f"<Vis  ({str(self.intent)}) mark: {self.mark}, score: {self.score} >"
		filter_spec = None
		channels, additional_channels = [], []
		for clause in self._inferred_intent:

			if hasattr(clause,"value"):
				if clause.value != "":
					filter_spec = clause
			if hasattr(clause,"attribute"):
				if clause.attribute != "":
					if clause.aggregation != "" and clause.aggregation is not None:
						attribute = clause._aggregation_name.upper() + "(" + clause.attribute + ")"
					elif clause.bin_size > 0:
						attribute = "BIN(" + clause.attribute + ")"
					else:
						attribute = clause.attribute
					if clause.channel == "x":
						channels.insert(0, [clause.channel, attribute])
					elif clause.channel == "y":
						channels.insert(1, [clause.channel, attribute])
					elif clause.channel != "":
						additional_channels.append([clause.channel, attribute])

		channels.extend(additional_channels)
		str_channels = ""
		for channel in channels:
			str_channels += channel[0] + ": " + channel[1] + ", "

		if filter_spec:
			return f"<Vis  ({str_channels[:-2]} -- [{filter_spec.attribute}{filter_spec.filter_op}{filter_spec.value}]) mark: {self.mark}, score: {self.score} >"
		else:
			return f"<Vis  ({str_channels[:-2]}) mark: {self.mark}, score: {self.score} >"
	def set_intent(self, intent:List[Clause]) -> None:
		"""
		Sets the intent of the Vis and refresh the source based on the new intent

		Parameters
		----------
		intent : List[Clause]
			Query specifying the desired VisList
		"""		
		self.intent = intent
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
					currentVis= LuxDataFrame.current_view_to_JSON([self]),
					recommendations=[],
					intent=""
				)
			display(widget)
	def get_attr_by_attr_name(self,attr_name):
		return list(filter(lambda x: x.attribute == attr_name, self._inferred_intent))
		
	def get_attr_by_channel(self, channel):
		spec_obj = list(filter(lambda x: x.channel == channel and x.value=='' if hasattr(x, "channel") else False, self._inferred_intent))
		return spec_obj

	def get_attr_by_data_model(self, dmodel, exclude_record=False):
		if (exclude_record):
			return list(filter(lambda x: x.data_model == dmodel and x.value=='' if x.attribute!="Record" and hasattr(x, "data_model") else False, self._inferred_intent))
		else:
			return list(filter(lambda x: x.data_model == dmodel and x.value=='' if hasattr(x, "data_model") else False, self._inferred_intent))

	def get_attr_by_data_type(self, dtype):
		return list(filter(lambda x: x.data_type == dtype and x.value=='' if hasattr(x, "data_type") else False, self._inferred_intent))

	def remove_filter_from_spec(self, value):
		new_intent = list(filter(lambda x: x.value != value, self._inferred_intent))
		self.set_intent(new_intent)
		
	def remove_column_from_spec(self, attribute, remove_first:bool=False):
		"""
		Removes an attribute from the Vis's clause

		Parameters
		----------
		attribute : str
			attribute to be removed
		remove_first : bool, optional
			Boolean flag to determine whether to remove all instances of the attribute or only one (first) instance, by default False
		"""		
		if (not remove_first):
			new_inferred = list(filter(lambda x: x.attribute != attribute, self._inferred_intent))
			self._inferred_intent = new_inferred
			self.intent = new_inferred
		elif (remove_first):
			new_inferred = []
			skip_check = False
			for i in range(0, len(self._inferred_intent)):
				if self._inferred_intent[i].value=="": # clause is type attribute
					column_spec = []
					column_names = self._inferred_intent[i].attribute
					# if only one variable in a column, columnName results in a string and not a list so
					# you need to differentiate the cases
					if isinstance(column_names, list):
						for column in column_names:
							if (column != attribute) or skip_check:
								column_spec.append(column)
							elif (remove_first):
								remove_first = True
						new_inferred.append(Clause(column_spec))
					else:
						if column_names != attribute or skip_check:
							new_inferred.append(Clause(attribute = column_names))
						elif (remove_first):
							skip_check = True
				else:
					new_inferred.append(self._inferred_intent[i])
			self.intent = new_inferred
			self._inferred_intent = new_inferred

	def to_Altair(self) -> str:
		"""
		Generate minimal Altair code to visualize the Vis

		Returns
		-------
		str
			String version of the Altair code. Need to print out the string to apply formatting.
		"""		
		from lux.vislib.altair.AltairRenderer import AltairRenderer
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
		from lux.vislib.altair.AltairRenderer import AltairRenderer
		renderer = AltairRenderer(output_type="VegaLite")
		self.code = renderer.create_vis(self)
		if (prettyOutput):
			return "** Remove this comment -- Copy Text Below to Vega Editor(vega.github.io/editor) to visualize and edit **\n"+json.dumps(self.code, indent=2)
		else:
			return self.code
		
	def render_VSpec(self, renderer="altair"):
		if (renderer == "altair"):
			return self.to_VegaLite(prettyOutput=False)
	
	def refresh_source(self, ldf):# -> Vis:
		"""
		Loading the source data into the Vis by instantiating the specification and 
		populating the Vis based on the source data, effectively "materializing" the Vis.

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
		lux.Vis.VisList.refresh_source

		Note
		----
		Function derives a new _inferred_intent by instantiating the intent specification on the new data
		"""		
		from lux.compiler.Parser import Parser
		from lux.compiler.Validator import Validator
		from lux.compiler.Compiler import Compiler
		from lux.executor.PandasExecutor import PandasExecutor #TODO: temporary (generalize to executor)
		self.source = ldf
		#TODO: handle case when user input vanilla Pandas dataframe
		self._inferred_intent = Parser.parse(self.intent)
		Validator.validate_spec(self._inferred_intent,ldf)
		vc = Compiler.compile(ldf,self._inferred_intent,[self],enumerate_collection=False)
		ldf.executor.execute(vc,ldf)
		# Copying properties over since we can not redefine `self` within class function
		vis = vc[0]
		self.title = vis.title
		self.mark = vis.mark
		self._inferred_intent = vis._inferred_intent
		self.data = vis.data
		self.min_max = vis.min_max