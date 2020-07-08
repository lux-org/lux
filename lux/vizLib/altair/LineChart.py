from lux.vizLib.altair.AltairChart import AltairChart
import altair as alt
alt.data_transformers.disable_max_rows()
class LineChart(AltairChart):
	"""
	LineChart is a subclass of AltairChart that render as a line charts.
	All rendering properties for line charts are set here.

	See Also
	--------
	altair-viz.github.io
	"""
	def __init__(self,dobj):
		super().__init__(dobj)
	def __repr__(self):
		return f"Line Chart <{str(self.view)}>"
	def initialize_chart(self):
		self.tooltip = False # tooltip looks weird for line chart
		x_attr = self.view.get_attr_by_channel("x")[0]
		y_attr = self.view.get_attr_by_channel("y")[0]


		self.code += "import altair as alt\n"
		self.code += "import pandas._libs.tslibs.timestamps\n"
		self.code += "from pandas._libs.tslibs.timestamps import Timestamp\n"
		self.code += f"viewData = pd.DataFrame({str(self.data.to_dict())})\n"
		
		if (y_attr.data_model == "measure"):
			agg_title = f"{y_attr.aggregation.capitalize()} of {y_attr.attribute}"
			x_attr_spec = alt.X(x_attr.attribute, type = x_attr.data_type)
			y_attr_spec = alt.Y(y_attr.attribute, type= y_attr.data_type, title=agg_title)
			x_attr_field_code = f"alt.X('{x_attr.attribute}', type = '{x_attr.data_type}')"
			y_attr_fieldCode = f"alt.Y('{y_attr.attribute}', type= '{y_attr.data_type}', title='{agg_title}')"
		else:
			agg_title = f"{x_attr.aggregation.capitalize()} of {x_attr.attribute}"
			x_attr_spec = alt.X(x_attr.attribute,type= x_attr.data_type, title=agg_title)
			y_attr_spec = alt.Y(y_attr.attribute, type = y_attr.data_type)
			x_attr_field_code = f"alt.X('{x_attr.attribute}', type = '{x_attr.data_type}', title='{agg_title}')"
			y_attr_fieldCode = f"alt.Y('{y_attr.attribute}', type= '{y_attr.data_type}')"

		chart = alt.Chart(self.data).mark_line().encode(
			    x = x_attr_spec,
			    y = y_attr_spec
			)
		chart = chart.interactive() # Enable Zooming and Panning
		self.code += f'''
		chart = alt.Chart(viewData).mark_line().encode(
		    y = {y_attr_fieldCode},
		    x = {x_attr_field_code},
		)
		chart = chart.interactive() # Enable Zooming and Panning
		'''
		return chart 
	