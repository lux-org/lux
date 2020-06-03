from lux.context.Spec import Spec
from lux.utils.utils import checkImportLuxWidget
class View:
	'''
	View Object represents a collection of fully fleshed out specifications required for data fetching and visualization.
	'''

	def __init__(self, specifiedSpecLst,title=""):
		self.specLst = specifiedSpecLst
		self.title = title
		self.mark = ""
		self.data = None
		self.score = 0.0
		self.vis = None
		self.xMinMax = {}
		self.yMinMax = {}

	def __repr__(self):
		x_channel = ""
		y_channel = ""
		filter_spec = None
		channels, additional_channels = [], []
		for spec in self.specLst:
			if spec.value != "":
				filter_spec = spec
			if spec.attribute != "":
				if spec.aggregation != "":
					attribute = spec.aggregation + "(" + spec.attribute + ")"
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
	def _repr_html_(self):
		from IPython.display import display
		checkImportLuxWidget()
		import luxWidget
		from lux.luxDataFrame.LuxDataframe import LuxDataFrame
		# widget  = LuxDataFrame.renderWidget(inputCurrentView=self,renderTarget="viewOnly")
		widget =  luxWidget.LuxWidget(
                currentView= LuxDataFrame.currentViewToJSON([self]),
                recommendations=[],
                context={}
            )
		display(widget)

	def getAttrByChannel(self, channel):
		specObj = list(filter(lambda x: x.channel == channel and x.value=='' if hasattr(x, "channel") else False, self.specLst))
		return specObj

	def getAttrByDataModel(self, dmodel):
		return list(filter(lambda x: x.dataModel == dmodel and x.value=='' if hasattr(x, "dataModel") else False, self.specLst))

	def getAttrByDataType(self, dtype):
		return list(filter(lambda x: x.dataType == dtype and x.value=='' if hasattr(x, "dataType") else False, self.specLst))

	def removeColumnFromSpec(self, attribute):
		self.spec = list(filter(lambda x: x.attribute != attribute, self.specLst))

	def removeColumnFromSpecNew(self, attribute):
		newSpec = []
		for i in range(0, len(self.specLst)):
			if self.specLst[i].value=="": # spec is type attribute
				columnSpec = []
				columnNames = self.specLst[i].attribute
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
				newSpec.append(self.specLst[i])
		self.specLst = newSpec

	def renderVSpec(self, renderer="altair"):
		from lux.vizLib.altair.AltairRenderer import AltairRenderer
		if (renderer == "altair"):
			renderer = AltairRenderer()
		self.vis= renderer.createVis(self)
		return self.vis
	'''
	Possibly add more helper functions for retrieving information fro specified SpecLst 
	'''
