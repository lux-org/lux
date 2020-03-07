import pandas as pd
import altair as alt
class AltairChart:
	"""
	AltairChart is a representation of a chart. 
	Common utilities for charts that is independent of chart types should go here.
	"""			
	def __init__(self, view):
		self.view = view
		# self.data = pd.read_json(view.data.to_json())
		# from vega_datasets import data
		# self.data = data.cars.url
		self.data = "chartData"
		self.tooltip = True
		self.chart = self.initializeChart()
		# self.addTooltip()
		self.encodeColor()
		self.addTitle()
	def __repr__(self):
		return f"AltairChart <{str(self.view)}>"
	def addTooltip(self):
		if (self.tooltip): 
			self.chart = self.chart.encode(tooltip=list(self.view.data.df.columns))
	def encodeColor(self):
		colorAttr = self.view.getObjFromChannel("color")
		if (len(colorAttr)==1):
			self.chart = self.chart.encode(color=alt.Color(colorAttr[0].attribute,type=colorAttr[0].dataType))
		elif (len(colorAttr)>1):
			raise ValueError("There should not be more than one attribute specified in the same channel.")
	def addTitle(self):
		chartTitle = self.view.title
		if chartTitle:
			self.chart = self.chart.encode().properties(
				title = chartTitle
			)
	def initializeChart(self):
		return NotImplemented