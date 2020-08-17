import pandas as pd
import altair as alt
from lux.utils.date_utils import compute_date_granularity
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
		self.data = view.data
		self.tooltip = True
		# ----- START self.code modification -----
		self.source_code = ""
		self.code = "" 
		self.chart = self.initialize_chart()
		# self.add_tooltip()
		self.encode_color()
		self.add_title()
		self.apply_default_config()

		# ----- END self.code modification -----
	def __repr__(self):
		return f"AltairChart <{str(self.view)}>"
	def add_tooltip(self):
		if (self.tooltip): 
			self.chart = self.chart.encode(tooltip=list(self.view.data.columns))

	def apply_default_config(self):
		self.chart = self.chart.configure_title(fontWeight=500,fontSize=13,font="Helvetica Neue")
		self.chart = self.chart.configure_axis(titleFontWeight=500,titleFontSize=11,titleFont="Helvetica Neue",
									labelFontWeight=400,labelFontSize=9,labelFont="Helvetica Neue",labelColor="#505050")
		self.chart = self.chart.configure_legend(titleFontWeight=500,titleFontSize=10,titleFont="Helvetica Neue",
									labelFontWeight=400,labelFontSize=9,labelFont="Helvetica Neue")
		self.chart = self.chart.properties(width=160,height=150)
		original_code = self.code
		def additional_code(df):
			chart = original_code(df)
			chart = chart.configure_title(fontWeight=500,fontSize=13,font='Helvetica Neue')
			chart = chart.configure_axis(titleFontWeight=500,titleFontSize=11,titleFont='Helvetica Neue', labelFontWeight=400,labelFontSize=8,labelFont='Helvetica Neue',labelColor='#505050')
			chart = chart.configure_legend(titleFontWeight=500,titleFontSize=10,titleFont='Helvetica Neue', labelFontWeight=400,labelFontSize=8,labelFont='Helvetica Neue')
			chart = chart.properties(width=160,height=150)
			return chart
		self.code = additional_code
		self.source_code+= "chart = chart.configure_title(fontWeight=500,fontSize=13,font='Helvetica Neue')\n"
		self.source_code+= "chart = chart.configure_axis(titleFontWeight=500,titleFontSize=11,titleFont='Helvetica Neue',\n"
		self.source_code+= "					labelFontWeight=400,labelFontSize=8,labelFont='Helvetica Neue',labelColor='#505050')\n"
		self.source_code+= "chart = chart.configure_legend(titleFontWeight=500,titleFontSize=10,titleFont='Helvetica Neue',\n"
		self.source_code+= "					labelFontWeight=400,labelFontSize=8,labelFont='Helvetica Neue')\n"
		self.source_code+= "chart = chart.properties(width=160,height=150)\n"

	def encode_color(self):
		color_attr = self.view.get_attr_by_channel("color")
		if (len(color_attr)==1):
			color_attr_name = color_attr[0].attribute
			color_attr_type = color_attr[0].data_type
			original_code = self.code
			if (color_attr_type=="temporal"):
				timeUnit = compute_date_granularity(self.view.data[color_attr_name])
				self.chart = self.chart.encode(color=alt.Color(color_attr_name,type=color_attr_type,timeUnit=timeUnit,title=color_attr_name))	
				def additional_code(df):
					chart = original_code(df)
					chart = chart.encode(color=alt.Color(color_attr_name,type=color_attr_type,timeUnit=timeUnit,title=color_attr_name))
					return chart
				self.code = additional_code
				self.source_code+=f"chart = chart.encode(color=alt.Color('{color_attr_name}',type='{color_attr_type}',timeUnit='{timeUnit}',title='{color_attr_name}'))"
			else:
				self.chart = self.chart.encode(color=alt.Color(color_attr_name,type=color_attr_type))
				def additional_code(df):
					chart = original_code(df)
					chart = chart.encode(color=alt.Color(color_attr_name,type=color_attr_type))
					return chart
				self.code = additional_code
				self.source_code+=f"chart = chart.encode(color=alt.Color('{color_attr_name}',type='{color_attr_type}'))\n"
		elif (len(color_attr)>1):
			raise ValueError("There should not be more than one attribute specified in the same channel.")
		
	def add_title(self):
		chart_title = self.view.title
		if chart_title:
			self.chart = self.chart.encode().properties(
				title = chart_title
			)
			if (self.code!=""):
				original_code = self.code
				def additional_code(df):
					chart = original_code(df)
					chart = chart.encode().properties(title = chart_title)
					return chart
				self.code = additional_code
				self.source_code+=f"chart = chart.encode().properties(title = '{chart_title}')"
	def initialize_chart(self):
		return NotImplemented
