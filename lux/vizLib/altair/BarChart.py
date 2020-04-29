from lux.vizLib.altair.AltairChart import AltairChart
import altair as alt
alt.data_transformers.disable_max_rows()
class BarChart(AltairChart):
	def __init__(self,dobj):
		super().__init__(dobj)
	def __repr__(self):
		return f"Bar Chart <{str(self.view)}>"
	def initializeChart(self):
		self.tooltip = False
		xAttr = self.view.getObjFromChannel("x")[0]
		yAttr = self.view.getObjFromChannel("y")[0]
		if (xAttr.dataModel == "measure"):
			yAttrField = alt.Y(yAttr.attribute, type = yAttr.dataType)
			xAttrField = alt.X(xAttr.attribute,type=xAttr.dataType,title=f"{xAttr.aggregation.capitalize()} of {xAttr.attribute}")
			if (yAttr.sort=="ascending"):
				yAttrField.sort="-x"
		else:
			xAttrField = alt.X(xAttr.attribute, type = xAttr.dataType)
			if (xAttr.sort=="ascending"):
				xAttrField.sort="-y"
			yAttrField = alt.Y(yAttr.attribute,type=yAttr.dataType,title=f"{yAttr.aggregation.capitalize()} of {yAttr.attribute}")
		chart = alt.Chart(self.data).mark_bar().encode(
			    y = yAttrField,
			    x = xAttrField
			)
		# TODO: tooltip messes up the count() bar charts
		chart = chart.configure_mark(tooltip=alt.TooltipContent('encoding')) # Setting tooltip as non-null
		# Can not do interactive whenever you have default count measure otherwise output strange error (Javascript Error: Cannot read property 'length' of undefined)
		#chart = chart.interactive() # If you want to enable Zooming and Panning
		return chart 
	