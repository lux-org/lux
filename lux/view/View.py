from __future__ import annotations
from typing import List, Callable
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
					elif spec.binSize > 0:
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
			return f"<View  ({str_channels[:-2]} -- [{filter_spec.attribute}{filter_spec.filterOp}{filter_spec.value}]) mark: {self.mark}, score: {self.score} >"
		else:
			return f"<View  ({str_channels[:-2]}) mark: {self.mark}, score: {self.score} >"
	def set_plot_config(self,configFunc:Callable):
		"""
		Modify plot aesthetic settings to the View
		Currently only supported for Altair visualizations

		Parameters
		----------
		configFunc : typing.Callable
			A function that takes in an AltairChart (https://altair-viz.github.io/user_guide/generated/toplevel/altair.Chart.html) as input and returns an AltairChart as output
		"""
		self.plot_config = configFunc
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
			# widget  = LuxDataFrame.render_widget(inputCurrentView=self,renderTarget="viewOnly")
			widget =  luxWidget.LuxWidget(
					currentView= LuxDataFrame.current_view_to_JSON([self]),
					recommendations=[],
					context={}
				)
			display(widget)
	def getAttrByAttrName(self,attrName):
		return list(filter(lambda x: x.attribute == attrName, self.spec_lst))
		
	def getAttrByChannel(self, channel):
		specObj = list(filter(lambda x: x.channel == channel and x.value=='' if hasattr(x, "channel") else False, self.spec_lst))
		return specObj

	def getAttrByDataModel(self, dmodel, excludeRecord=False):
		if (excludeRecord):
			return list(filter(lambda x: x.data_model == dmodel and x.value=='' if x.attribute!="Record" and hasattr(x, "data_model") else False, self.spec_lst))
		else:
			return list(filter(lambda x: x.data_model == dmodel and x.value=='' if hasattr(x, "data_model") else False, self.spec_lst))

	def getAttrByDataType(self, dtype):
		return list(filter(lambda x: x.data_type == dtype and x.value=='' if hasattr(x, "data_type") else False, self.spec_lst))

	def removeColumnFromSpec(self, attribute):
		self.spec = list(filter(lambda x: x.attribute != attribute, self.spec_lst))

	def removeColumnFromSpecNew(self, attribute):
		newSpec = []
		for i in range(0, len(self.spec_lst)):
			if self.spec_lst[i].value=="": # spec is type attribute
				columnSpec = []
				columnNames = self.spec_lst[i].attribute
				# if only one variable in a column, columnName results in a string and not a list so
				# you need to differentiate the cases
				if isinstance(columnNames, list):
					for column in columnNames:
						if column != attribute:
							columnSpec.append(column)
					newSpec.append(Spec(columnSpec))
				else:
					if columnNames != attribute:
						newSpec.append(Spec(attribute = columnNames))
			else:
				newSpec.append(self.spec_lst[i])
		self.spec_lst = newSpec
	def toAltair(self) -> str:
		"""
		Generate minimal Altair code to visualize the view

		Returns
		-------
		str
			String version of the Altair code. Need to print out the string to apply formatting.
		"""		
		from lux.vizLib.altair.AltairRenderer import AltairRenderer
		renderer = AltairRenderer(outputType="Altair")
		self.vis= renderer.createVis(self)
		return self.vis

	def toVegaLite(self) -> dict:
		"""
		Generate minimal VegaLite code to visualize the view

		Returns
		-------
		dict
			Dictionary of the VegaLite JSON specification
		"""		
		from lux.vizLib.altair.AltairRenderer import AltairRenderer
		renderer = AltairRenderer(outputType="VegaLite")
		self.vis = renderer.createVis(self)
		return self.vis
		
	def render_VSpec(self, renderer="altair"):
		if (renderer == "altair"):
			return self.toVegaLite()
	
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
		vc = Compiler.compile(ldf,ldf.context,[self],enumerateCollection=False)
		PandasExecutor.execute(vc,ldf)
		return vc[0]