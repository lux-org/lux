from lux.vizLib.altair.AltairChart import AltairChart
import altair as alt
alt.data_transformers.disable_max_rows()
class BarChart(AltairChart):
	def __init__(self,dobj):
		super().__init__(dobj)
	def __repr__(self):
		return f"Bar Chart <{str(self.dobj)}>"
	def initializeChart(self):
		self.tooltip = False
		xAttr = self.dobj.getObjFromChannel("x")[0]
		yAttr = self.dobj.getObjFromChannel("y")[0]
		if (xAttr.dataModel == "measure"):
			yAttrField = alt.Y(yAttr.columnName, type = "nominal",sort="-x")
			xAttrField = alt.X(xAttr.columnName,type="quantitative", aggregate="mean")#TODO: fix to non-default aggregate function
		else:
			xAttrField = alt.X(xAttr.columnName, type = "nominal",sort="-y")
			yAttrField = alt.Y(yAttr.columnName,type="quantitative", aggregate="mean")#TODO: fix to non-default aggregate function
		if (yAttr.columnName=="count()"):
			yAttrField = alt.Y("Record",type="quantitative", aggregate="count")
		if (xAttr.columnName=="count()"):
			xAttrField = alt.X("Record",type="quantitative", aggregate="count")
		chart = alt.Chart(self.dataURL).mark_bar().encode(
			    y = yAttrField,
			    x = xAttrField
			)
		# TODO: tooltip messes up the count() bar charts
		# chart = chart.configure_mark(tooltip=alt.TooltipContent('encoding')) # Setting tooltip as non-null
		# Can not do interactive whenever you have default count measure otherwise output strange error (Javascript Error: Cannot read property 'length' of undefined)
		#chart = chart.interactive() # If you want to enable Zooming and Panning
		return chart 
	