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
		xAttr = self.view.getAttrByChannel("x")[0]
		# print(xAttr.attribute)
		xMin = self.view.xMinMax[xAttr.attribute][0]
		xMax = self.view.xMinMax[xAttr.attribute][1]

		chart = alt.Chart(self.data).mark_bar(size=12).encode(
			alt.X(xAttr.attribute, type=xAttr.dataType, axis=alt.Axis(labelOverlap=True), scale=alt.Scale(domain=(xMin, xMax))),#, bin=alt.Bin(maxbins=50)),
			alt.Y("Count of Records (binned)", type="quantitative")
		)
		return chart 