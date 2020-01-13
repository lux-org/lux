from lux.vizLib.altair.AltairChart import AltairChart
import altair as alt
alt.data_transformers.disable_max_rows()
class LineChart(AltairChart):
	def __init__(self,dobj):
		super().__init__(dobj)
	def __repr__(self):
		return f"Line Chart <{str(self.dobj)}>"
	def initializeChart(self):
		self.tooltip = False # tooltip looks weird for line chart
		xAttr = self.dobj.getObjFromChannel("x")[0]
		yAttr = self.dobj.getObjFromChannel("y")[0]
		if (yAttr.dataModel == "measure"):		
			xAttrSpec = alt.X(xAttr.columnName, type = "ordinal")
			yAttrSpec = alt.Y(yAttr.columnName,type="quantitative", aggregate="mean")
		else:
			xAttrSpec = alt.X(xAttr.columnName,type="quantitative", aggregate="mean")
			yAttrSpec = alt.Y(yAttr.columnName, type = "ordinal")
		if (yAttr.columnName=="count()"):
			yAttrSpec = alt.Y("Record",type="quantitative", aggregate="count")
		chart = alt.Chart(self.dataURL).mark_line().encode(
			    x = xAttrSpec,
			    # TODO: need to change aggregate to non-default function, read aggFunc info in somewhere
			    y = yAttrSpec
			)
		chart = chart.interactive() # If you want to enable Zooming and Panning
		return chart 
	