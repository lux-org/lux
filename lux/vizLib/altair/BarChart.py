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

		self.code += "import altair as alt\n"
		# self.code += f"viewData = pd.DataFrame({str(self.data.to_dict(orient='records'))})\n"
		self.code += f"viewData = pd.DataFrame({str(self.data.to_dict())})\n"

		if (xAttr.data_model == "measure"):
			aggTitle = f'{xAttr.aggregation.capitalize()} of {xAttr.attribute}'
			yAttrField = alt.Y(yAttr.attribute, type= yAttr.data_type, axis=alt.Axis(labelOverlap=True))
			xAttrField = alt.X(xAttr.attribute, type= xAttr.data_type, title=aggTitle)
			yAttrFieldCode = f"alt.Y('{yAttr.attribute}', type= '{yAttr.data_type}', axis=alt.Axis(labelOverlap=True))"
			xAttrFieldCode = f"alt.X('{xAttr.attribute}', type= '{xAttr.data_type}', title='{aggTitle}')"

			if (yAttr.sort=="ascending"):
				yAttrField.sort="-x"
				yAttrFieldCode = f"alt.Y('{yAttr.attribute}', type= '{yAttr.data_type}', axis=alt.Axis(labelOverlap=True), sort ='-x')"
		else:
			aggTitle = f"{yAttr.aggregation.capitalize()} of {yAttr.attribute}"
			xAttrField = alt.X(xAttr.attribute, type = xAttr.data_type,axis=alt.Axis(labelOverlap=True))
			yAttrField = alt.Y(yAttr.attribute,type=yAttr.data_type,title=aggTitle)
			xAttrFieldCode = f"alt.X('{xAttr.attribute}', type= '{xAttr.data_type}', axis=alt.Axis(labelOverlap=True))"
			yAttrFieldCode = f"alt.Y('{yAttr.attribute}', type= '{yAttr.data_type}', title='{aggTitle}')"
			if (xAttr.sort=="ascending"):
				xAttrField.sort="-y"
				xAttrFieldCode = f"alt.X('{xAttr.attribute}', type= '{xAttr.data_type}', axis=alt.Axis(labelOverlap=True),sort='-y')"
			
		chart = alt.Chart(self.data).mark_bar().encode(
			    y = yAttrField,
			    x = xAttrField
			)
		# TODO: tooltip messes up the count() bar charts		
		# Can not do interactive whenever you have default count measure otherwise output strange error (Javascript Error: Cannot read property 'length' of undefined)
		#chart = chart.interactive() # If you want to enable Zooming and Panning
		chart = chart.configure_mark(tooltip=alt.TooltipContent('encoding')) # Setting tooltip as non-null

		self.code += f'''
		chart = alt.Chart(viewData).mark_bar(size=12).encode(
		    y = {yAttrFieldCode},
		    x = {xAttrFieldCode},
		)
		chart = chart.configure_mark(tooltip=alt.TooltipContent('encoding')) # Setting tooltip as non-null
		'''
		return chart 