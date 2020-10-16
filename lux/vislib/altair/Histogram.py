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
class Histogram(AltairChart):
	"""
	Histogram is a subclass of AltairChart that render as a histograms.
	All rendering properties for histograms are set here.

	See Also
	--------
	altair-viz.github.io
	"""
	def __init__(self,vis):
		super().__init__(vis)
	def __repr__(self):
		return f"Histogram <{str(self.vis)}>"
	def initialize_chart(self):
		self.tooltip = False
		measure = self.vis.get_attr_by_data_model("measure",exclude_record=True)[0]
		msr_attr = self.vis.get_attr_by_channel(measure.channel)[0]
		x_min = self.vis.min_max[msr_attr.attribute][0]
		x_max = self.vis.min_max[msr_attr.attribute][1]

		x_range = abs(max(self.vis.data[msr_attr.attribute]) - 
			min(self.vis.data[msr_attr.attribute]))
		plot_range = abs(x_max - x_min)
		markbar = x_range / plot_range * 12

		if (measure.channel=="x"):	
			chart = alt.Chart(self.data).mark_bar(size=markbar).encode(
				alt.X(msr_attr.attribute, title=f'{msr_attr.attribute} (binned)',bin=alt.Bin(binned=True), type=msr_attr.data_type, axis=alt.Axis(labelOverlap=True), scale=alt.Scale(domain=(x_min, x_max))),
				alt.Y("Number of Records", type="quantitative")
			)
		elif (measure.channel=="y"):
			chart = alt.Chart(self.data).mark_bar(size=markbar).encode(
				x = alt.X("Number of Records", type="quantitative"),
				y = alt.Y(msr_attr.attribute, title=f'{msr_attr.attribute} (binned)', bin=alt.Bin(binned=True), axis=alt.Axis(labelOverlap=True), scale=alt.Scale(domain=(x_min, x_max)))
			)
		#####################################
		## Constructing Altair Code String ##
		#####################################
		
		self.code += "import altair as alt\n"
		# self.code += f"visData = pd.DataFrame({str(self.data.to_dict(orient='records'))})\n"
		self.code += f"visData = pd.DataFrame({str(self.data.to_dict())})\n"
		if (measure.channel=="x"):	
			self.code += f'''
		chart = alt.Chart(visData).mark_bar(size={markbar}).encode(
		    alt.X('{msr_attr.attribute}', title='{msr_attr.attribute} (binned)',bin=alt.Bin(binned=True), type='{msr_attr.data_type}', axis=alt.Axis(labelOverlap=True), scale=alt.Scale(domain=({x_min}, {x_max}))),
		    alt.Y("Number of Records", type="quantitative")
		)
		'''
		elif (measure.channel=="y"):
			self.code += f'''
		chart = alt.Chart(visData).mark_bar(size={markbar}).encode(
		    alt.Y('{msr_attr.attribute}', title='{msr_attr.attribute} (binned)',bin=alt.Bin(binned=True), type='{msr_attr.data_type}', axis=alt.Axis(labelOverlap=True), scale=alt.Scale(domain=({x_min}, {x_max}))),
		    alt.X("Number of Records", type="quantitative")
		)
		'''
		return chart 