#  Copyright 2019-2020 The Lux Authors.
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from lux.vislib.altair.AltairChart import AltairChart
import altair as alt
alt.data_transformers.disable_max_rows()
from lux.utils.utils  import get_agg_title
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
		return f"Bar Chart <{str(self.vis)}>"
	def initialize_chart(self):
		self.tooltip = False
		x_attr = self.vis.get_attr_by_channel("x")[0]
		y_attr = self.vis.get_attr_by_channel("y")[0]
		
		if (x_attr.data_model == "measure"):
			agg_title = get_agg_title(x_attr)
			measure_attr = x_attr.attribute
			y_attr_field = alt.Y(y_attr.attribute, type= y_attr.data_type, axis=alt.Axis(labelOverlap=True))
			x_attr_field = alt.X(x_attr.attribute, type= x_attr.data_type, title=agg_title)
			y_attr_field_code = f"alt.Y('{y_attr.attribute}', type= '{y_attr.data_type}', axis=alt.Axis(labelOverlap=True))"
			x_attr_field_code = f"alt.X('{x_attr.attribute}', type= '{x_attr.data_type}', title='{agg_title}')"

			if (y_attr.sort=="ascending"):
				y_attr_field.sort="-x"
				y_attr_field_code = f"alt.Y('{y_attr.attribute}', type= '{y_attr.data_type}', axis=alt.Axis(labelOverlap=True), sort ='-x')"
		else:
			agg_title = get_agg_title(y_attr)
			measure_attr = y_attr.attribute
			x_attr_field = alt.X(x_attr.attribute, type = x_attr.data_type,axis=alt.Axis(labelOverlap=True))
			y_attr_field = alt.Y(y_attr.attribute,type=y_attr.data_type,title=agg_title)
			x_attr_field_code = f"alt.X('{x_attr.attribute}', type= '{x_attr.data_type}', axis=alt.Axis(labelOverlap=True))"
			y_attr_field_code = f"alt.Y('{y_attr.attribute}', type= '{y_attr.data_type}', title='{agg_title}')"
			if (x_attr.sort=="ascending"):
				x_attr_field.sort="-y"
				x_attr_field_code = f"alt.X('{x_attr.attribute}', type= '{x_attr.data_type}', axis=alt.Axis(labelOverlap=True),sort='-y')"
		
		k=10
		topK_code = ""
		if len(self.data)>k: # Truncating to only top k
			remaining_bars = len(self.data)-k
			self.data = self.data.nlargest(k,measure_attr)
			text = alt.Chart(self.data).mark_text(
				x=155, 
				y=142,
				align="right",
				color = "#ff8e04",
				fontSize = 11,
				text=f"+ {remaining_bars} more ..."
			)

			topK_code = f'''text = alt.Chart(visData).mark_text(
			x=155, 
			y=142,
			align="right",
			color = "#ff8e04",
			fontSize = 11,
			text=f"+ {remaining_bars} more ..."
		)
		chart = chart + text
			'''
		
		chart = alt.Chart(self.data).mark_bar().encode(
			    y = y_attr_field,
			    x = x_attr_field
			)
		if (topK_code!=""):
			chart = chart + text
		# TODO: tooltip messes up the count() bar charts		
		# Can not do interactive whenever you have default count measure otherwise output strange error (Javascript Error: Cannot read property 'length' of undefined)
		#chart = chart.interactive() # If you want to enable Zooming and Panning
		chart = chart.configure_mark(tooltip=alt.TooltipContent('encoding')) # Setting tooltip as non-null

		self.code += "import altair as alt\n"
		# self.code += f"visData = pd.DataFrame({str(self.data.to_dict(orient='records'))})\n"
		self.code += f"visData = pd.DataFrame({str(self.data.to_dict())})\n"
		self.code += f'''
		chart = alt.Chart(visData).mark_bar().encode(
		    y = {y_attr_field_code},
		    x = {x_attr_field_code},
		)
		{topK_code}
		chart = chart.configure_mark(tooltip=alt.TooltipContent('encoding')) # Setting tooltip as non-null
		'''
		return chart 