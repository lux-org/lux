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

		xRange = abs(max(self.view.data[msrAttr.attribute]) - 
			min(self.view.data[msrAttr.attribute]))
		plotRange = abs(xMax - xMin)
		markbar = xRange / plotRange * 12

		if (measure.channel=="x"):	
			chart = alt.Chart(self.data).mark_bar(size=markbar).encode(
				alt.X(msrAttr.attribute, title=f'{msrAttr.attribute} (binned)',bin=alt.Bin(binned=True), type=msrAttr.dataType, axis=alt.Axis(labelOverlap=True), scale=alt.Scale(domain=(xMin, xMax))),
				alt.Y("Count of Records", type="quantitative")
			)
		elif (measure.channel=="y"):
			chart = alt.Chart(self.data).mark_bar(size=markbar).encode(
				x = alt.X("Count of Records", type="quantitative"),
				y = alt.Y(msrAttr.attribute, title=f'{msrAttr.attribute} (binned)', bin=alt.Bin(binned=True), axis=alt.Axis(labelOverlap=True), scale=alt.Scale(domain=(xMin, xMax)))
			)
		#####################################
		## Constructing Altair Code String ##
		#####################################
		
		self.code += "import altair as alt\n"
		# self.code += f"viewData = pd.DataFrame({str(self.data.to_dict(orient='records'))})\n"
		self.code += f"viewData = pd.DataFrame({str(self.data.to_dict())})\n"
		if (measure.channel=="x"):	
			self.code += f'''
		chart = alt.Chart(viewData).mark_bar(size=12).encode(
		    alt.X('{msrAttr.attribute}', title=f'{msrAttr.attribute} (binned)',bin=alt.Bin(binned=True), type='{msrAttr.dataType}', axis=alt.Axis(labelOverlap=True), scale=alt.Scale(domain=({xMin}, {xMax}))),
		    alt.Y("Count of Records", type="quantitative")
		)
		'''
		elif (measure.channel=="y"):
			self.code += f'''
		chart = alt.Chart(viewData).mark_bar(size=12).encode(
		    alt.Y('{msrAttr.attribute}', title=f'{msrAttr.attribute} (binned)',bin=alt.Bin(binned=True), type='{msrAttr.dataType}', axis=alt.Axis(labelOverlap=True), scale=alt.Scale(domain=({xMin}, {xMax}))),
		    alt.X("Count of Records", type="quantitative")
		)
		'''
		return chart 