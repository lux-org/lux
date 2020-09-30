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
class Heatmap(AltairChart):
	"""
	Heatmap is a subclass of AltairChart that render as a heatmap.
	All rendering properties for heatmap are set here.

	See Also
	--------
	altair-viz.github.io
	"""
	def __init__(self,vis):
		super().__init__(vis)
	def __repr__(self):
		return f"Heatmap <{str(self.vis)}>"
	def initialize_chart(self):
		# return NotImplemented
		x_attr = self.vis.get_attr_by_channel("x")[0]
		y_attr = self.vis.get_attr_by_channel("y")[0]
		# x_min = self.vis.min_max[x_attr.attribute][0]
		# x_max = self.vis.min_max[x_attr.attribute][1]

		# y_min = self.vis.min_max[y_attr.attribute][0]
		# y_max = self.vis.min_max[y_attr.attribute][1]

		chart = alt.Chart(self.data).mark_rect().encode(
			x=alt.X('xBinStart', type='quantitative', axis=alt.Axis(title=x_attr.attribute), bin = alt.BinParams(binned=True)),
			x2=alt.X2('xBinEnd'),
			y=alt.Y('yBinStart', type='quantitative', axis=alt.Axis(title=y_attr.attribute), bin = alt.BinParams(binned=True)),
			y2=alt.Y2('yBinEnd'),
			#opacity = alt.Opacity('z',type='quantitative',scale=alt.Scale(type="log"))
			color = alt.Color('z',type='quantitative', scale=alt.Scale(scheme='blues',type="log"),legend=None)
		)
		chart = chart.configure_mark(tooltip=alt.TooltipContent('encoding')) # Setting tooltip as non-null
		chart = chart.interactive() # Enable Zooming and Panning

		####################################
		# Constructing Altair Code String ##
		####################################
		
		self.code += "import altair as alt\n"
		# self.code += f"visData = pd.DataFrame({str(self.data.to_dict(orient='records'))})\n"
		self.code += f"visData = pd.DataFrame({str(self.data.to_dict())})\n"
		self.code += f'''
		chart = alt.Chart(visData).mark_rect().encode(
			x=alt.X('xBinStart', type='quantitative', axis=alt.Axis(title='{x_attr.attribute}'), bin = alt.BinParams(binned=True)),
			x2=alt.X2('xBinEnd'),
			y=alt.Y('yBinStart', type='quantitative', axis=alt.Axis(title='{y_attr.attribute}'), bin = alt.BinParams(binned=True)),
			y2=alt.Y2('yBinEnd'),
			#opacity = alt.Opacity('z',type='quantitative',scale=alt.Scale(type="log"))
			color = alt.Color('z',type='quantitative', scale=alt.Scale(scheme='blues',type="log"),legend=None)
		)
		chart = chart.configure_mark(tooltip=alt.TooltipContent('encoding')) # Setting tooltip as non-null
		'''
		return chart 