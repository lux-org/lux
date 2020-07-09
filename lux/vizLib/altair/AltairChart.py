import pandas as pd
import altair as alt
class AltairChart:
	"""
	AltairChart is a representation of a chart. 
	Common utilities for charts that is independent of chart types should go here.

	See Also
	--------
	altair-viz.github.io

	"""			
	def __init__(self, view):
		self.view = view
		# self.data = pd.read_json(view.data.to_json())
		# from vega_datasets import data
		# self.data = data.cars.url
		# self.data = "chartData"
		self.data = view.data
		self.tooltip = True
		# ----- START self.code modification -----
		self.code = "" 
		self.chart = self.initialize_chart()
		# self.add_tooltip()
		self.encode_color()
		self.add_title()
		# ----- END self.code modification -----
	def __repr__(self):
		return f"AltairChart <{str(self.view)}>"
	def add_tooltip(self):
		if (self.tooltip): 
			self.chart = self.chart.encode(tooltip=list(self.view.data.columns))
	def encode_color(self):
		color_attr = self.view.get_attr_by_channel("color")
		if (len(color_attr)==1):
			self.chart = self.chart.encode(color=alt.Color(color_attr[0].attribute,type=color_attr[0].data_type))
			self.code+=f"chart = chart.encode(color=alt.Color('{color_attr[0].attribute}',type='{color_attr[0].data_type}'))"
		elif (len(color_attr)>1):
			raise ValueError("There should not be more than one attribute specified in the same channel.")
		
	def add_title(self):
		chart_title = self.view.title
		if chart_title:
			self.chart = self.chart.encode().properties(
				title = chart_title
			)
			if (self.code!=""):
				self.code+=f"chart = chart.encode().properties(title = '{chart_title}')"
	def initialize_chart(self):
		return NotImplemented
