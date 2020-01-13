from lux.vizLib.altair.AltairChart import AltairChart
import altair as alt
alt.data_transformers.disable_max_rows()
class ScatterChart(AltairChart):
	def __init__(self,dobj):
		super().__init__(dobj)
	def __repr__(self):
		return f"ScatterChart <{str(self.dobj)}>"
	def initializeChart(self):
		# UP TO HERE: Broken because self.expandUnderspecified() in dataObj does not run when there are multiple object, we should not rely on spec
		# measures = list(filter(lambda x: x.dataModel=="measure" if hasattr(x,"dataModel") else False,self.dobj.spec))
		xAttr = self.dobj.getObjFromChannel("x")[0].columnName
		yAttr = self.dobj.getObjFromChannel("y")[0].columnName
		chart = alt.Chart(self.dataURL).mark_circle().encode(
		    x=alt.X(xAttr,scale=alt.Scale(zero=False)),
		    y=alt.Y(yAttr,scale=alt.Scale(zero=False))
		)
		chart = chart.configure_mark(tooltip=alt.TooltipContent('encoding')) # Setting tooltip as non-null
		chart = chart.interactive() # If you want to enable Zooming and Panning

		return chart 