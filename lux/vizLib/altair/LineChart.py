from lux.vizLib.altair.AltairChart import AltairChart
import altair as alt
alt.data_transformers.disable_max_rows()
class LineChart(AltairChart):
	"""
	LineChart is a subclass of AltairChart that render as a line charts.
	All rendering properties for line charts are set here.

	See Also
	--------
	altair-viz.github.io
	"""
	def __init__(self,dobj):
		super().__init__(dobj)
	def __repr__(self):
		return f"Line Chart <{str(self.view)}>"
	def initializeChart(self):
		self.tooltip = False # tooltip looks weird for line chart
		xAttr = self.view.getAttrByChannel("x")[0]
		yAttr = self.view.getAttrByChannel("y")[0]


		self.code += "import altair as alt\n"
		self.code += "import pandas._libs.tslibs.timestamps\n"
		self.code += "from pandas._libs.tslibs.timestamps import Timestamp\n"
		self.code += f"viewData = pd.DataFrame({str(self.data.to_dict())})\n"
		
		if (yAttr.dataModel == "measure"):
			aggTitle = f"{yAttr.aggregation.capitalize()} of {yAttr.attribute}"
			xAttrSpec = alt.X(xAttr.attribute, type = xAttr.dataType)
			yAttrSpec = alt.Y(yAttr.attribute, type= yAttr.dataType, title=aggTitle)
			xAttrFieldCode = f"alt.X('{xAttr.attribute}', type = '{xAttr.dataType}')"
			yAttrFieldCode = f"alt.Y('{yAttr.attribute}', type= '{yAttr.dataType}', title='{aggTitle}')"
		else:
			aggTitle = f"{xAttr.aggregation.capitalize()} of {xAttr.attribute}"
			xAttrSpec = alt.X(xAttr.attribute,type= xAttr.dataType, title=aggTitle)
			yAttrSpec = alt.Y(yAttr.attribute, type = yAttr.dataType)
			xAttrFieldCode = f"alt.X('{xAttr.attribute}', type = '{xAttr.dataType}', title='{aggTitle}')"
			yAttrFieldCode = f"alt.Y('{yAttr.attribute}', type= '{yAttr.dataType}')"

		chart = alt.Chart(self.data).mark_line().encode(
			    x = xAttrSpec,
			    y = yAttrSpec
			)
		chart = chart.interactive() # Enable Zooming and Panning
		self.code += f'''
		chart = alt.Chart(viewData).mark_line().encode(
		    y = {yAttrFieldCode},
		    x = {xAttrFieldCode},
		)
		chart = chart.interactive() # Enable Zooming and Panning
		'''
		return chart 
	