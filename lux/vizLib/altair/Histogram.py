from lux.vizLib.altair.AltairChart import AltairChart
import altair as alt
alt.data_transformers.disable_max_rows()
class Histogram(AltairChart):
	"""
	Histogram is a subclass of AltairChart that render as a histograms.
	All rendering properties for histograms are set here.

	See Also
	--------
	altair-viz.github.io
	"""
	def __init__(self,view):
		super().__init__(view)
	def __repr__(self):
		return f"Histogram <{str(self.view)}>"
	def initializeChart(self):
		self.tooltip = False
		measure = self.view.getAttrByDataModel("measure",excludeRecord=True)[0]
		msrAttr = self.view.getAttrByChannel(measure.channel)[0]
		xMin = self.view.xMinMax[msrAttr.attribute][0]
		xMax = self.view.xMinMax[msrAttr.attribute][1]
		if (measure.channel=="x"):	
			chart = alt.Chart(self.data).mark_bar(size=12).encode(
				alt.X(msrAttr.attribute, title=f'{msrAttr.attribute} (binned)',bin=alt.Bin(binned=True), type=msrAttr.dataType, axis=alt.Axis(labelOverlap=True), scale=alt.Scale(domain=(xMin, xMax))),
				alt.Y("Count of Records", type="quantitative")
			)
		else:
			chart = alt.Chart(self.data).mark_bar(size=12).encode(
				x = alt.X("Count of Records", type="quantitative"),
				y = alt.Y(msrAttr.attribute, title=f'{msrAttr.attribute} (binned)', bin=alt.Bin(binned=True), axis=alt.Axis(labelOverlap=True), scale=alt.Scale(domain=(xMin, xMax)))
			)
		return chart 