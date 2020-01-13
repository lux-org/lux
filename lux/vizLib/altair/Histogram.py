from lux.vizLib.altair.AltairChart import AltairChart
import altair as alt
alt.data_transformers.disable_max_rows()
class Histogram(AltairChart):
	def __init__(self,dobj):
		super().__init__(dobj)
	def __repr__(self):
		return f"Histogram <{str(self.dobj)}>"
	def initializeChart(self):
		self.tooltip = False
		xAttr = self.dobj.getObjFromChannel("x")[0].columnName
		yAttr = self.dobj.getObjFromChannel("y")[0].columnName
		#measures = list(filter(lambda x: x.dataModel=="measure" if hasattr(x,"dataModel") else False,self.dobj.spec))
		if (yAttr=="count()"):
			chart = alt.Chart(self.dataURL).mark_bar().encode(
				alt.X(xAttr, type="quantitative", bin=alt.Bin(maxbins=50)),
				alt.Y(yAttr)
			)
		else:
			chart = alt.Chart(self.dataURL).mark_bar().encode(
				alt.X(xAttr),
				alt.Y(yAttr, type="quantitative", bin=alt.Bin(maxbins=50))
			)
		return chart 