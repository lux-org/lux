from lux.vizLib.altair.AltairChart import AltairChart
import altair as alt
alt.data_transformers.disable_max_rows()
class BarChart(AltairChart):
	"""
	BarChart is a subclass of AltairChart that render as a bar charts.
	All rendering properties for bar charts are set here.

	See Also
	--------
	altair-viz.github.io
	"""
	def __init__(self,dobj):
		super().__init__(dobj)
	def __repr__(self):
		return f"Bar Chart <{str(self.view)}>"
	def initializeChart(self):
		self.tooltip = False
		xAttr = self.view.getAttrByChannel("x")[0]
		yAttr = self.view.getAttrByChannel("y")[0]

		print(self.data[xAttr.attribute].max())

		# does not work
		xMax = self.data[xAttr.attribute].max()

		if (xAttr.dataModel == "measure"):
			yAttrField = alt.Y(yAttr.attribute, type = yAttr.dataType, axis=alt.Axis(labelOverlap=True))
			xAttrField = alt.X(xAttr.attribute,scale=alt.Scale(domain=(0, xMax)), type=xAttr.dataType,title=f"{xAttr.aggregation.capitalize()} of {xAttr.attribute}")
			if (yAttr.sort=="ascending"):
				yAttrField.sort="-x"
		else:
			xAttrField = alt.X(xAttr.attribute, type = xAttr.dataType,axis=alt.Axis(labelOverlap=True))
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
	def getChartCode(self):
		return '''
		import altair as alt
		# Altair code placeholder
		'''