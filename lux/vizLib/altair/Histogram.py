from lux.vizLib.altair.AltairChart import AltairChart
import altair as alt
alt.data_transformers.disable_max_rows()
class Histogram(AltairChart):
	def __init__(self,view):
		super().__init__(view)
	def __repr__(self):
		return f"Histogram <{str(self.view)}>"
	def initializeChart(self):
		self.tooltip = False
		xAttr = self.view.getObjFromChannel("x")[0].attribute
		yAttr = self.view.getObjFromChannel("y")[0].attribute
		#measures = list(filter(lambda x: x.dataModel=="measure" if hasattr(x,"dataModel") else False,self.view.spec))
		if (yAttr=="count()"):
			chart = alt.Chart(self.data).mark_bar().encode(
				alt.X(xAttr, type="quantitative", bin=alt.Bin(maxbins=50)),
				alt.Y(yAttr, type="quantitative")
			)
		else:
			chart = alt.Chart(self.data).mark_bar().encode(
				alt.X(xAttr, type="quantitative"),
				alt.Y(yAttr, type="quantitative", bin=alt.Bin(maxbins=50))
			)
		return chart 