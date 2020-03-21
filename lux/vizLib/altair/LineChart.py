from lux.vizLib.altair.AltairChart import AltairChart
import altair as alt
alt.data_transformers.disable_max_rows()
class LineChart(AltairChart):
	def __init__(self,dobj):
		super().__init__(dobj)
	def __repr__(self):
		return f"Line Chart <{str(self.view)}>"
	def initializeChart(self):
		self.tooltip = False # tooltip looks weird for line chart
		xAttr = self.view.getObjFromChannel("x")[0]
		yAttr = self.view.getObjFromChannel("y")[0]
		
		if (yAttr.dataModel == "measure"):		
			xAttrSpec = alt.X(xAttr.attribute, type = "ordinal")
			yAttrSpec = alt.Y(yAttr.attribute,type="quantitative", aggregate=yAttr.aggregation)
		else:
			xAttrSpec = alt.X(xAttr.attribute,type="quantitative", aggregate=xAttr.aggregation)
			yAttrSpec = alt.Y(yAttr.attribute, type = "ordinal")
		# if (yAttr.attribute=="count()"):
		# 	yAttrSpec = alt.Y("Count of Records",type="quantitative", aggregate="count")
		chart = alt.Chart(self.data).mark_line().encode(
			    x = xAttrSpec,
			    # TODO: need to change aggregate to non-default function, read aggFunc info in somewhere
			    y = yAttrSpec
			)
		chart = chart.interactive() # If you want to enable Zooming and Panning
		return chart 
	