from lux.vizLib.altair.AltairChart import AltairChart
import altair as alt 
alt.data_transformers.disable_max_rows()
class ScatterChart(AltairChart):
	def __init__(self,dobj):
		super().__init__(dobj)
	def __repr__(self):
		return f"ScatterChart <{str(self.view)}>"
	def initializeChart(self):
		xAttr = self.view.getObjFromChannel("x")[0].attribute
		yAttr = self.view.getObjFromChannel("y")[0].attribute

		chart = alt.Chart(self.data).mark_circle().encode(
		    x=alt.X(xAttr,scale=alt.Scale(zero=False),type="quantitative"),
		    y=alt.Y(yAttr,scale=alt.Scale(zero=False),type="quantitative")
		)
		chart = chart.configure_mark(tooltip=alt.TooltipContent('encoding')) # Setting tooltip as non-null
		chart = chart.interactive() # If you want to enable Zooming and Panning

		return chart 