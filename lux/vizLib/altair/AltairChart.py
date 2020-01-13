class AltairChart:
	'''
	Chart Object represents one Altair chart
	The common utilities for charts (independent of chart types) should go here.
	'''
	def __init__(self, dobj):
		self.dobj = dobj
		self.dataURL = self.dobj.dataset.df#"chartData"
		self.tooltip = True
		self.chart = self.initializeChart()
		self.addTooltip()
		self.encodeColor()
		self.addTitle()
	def __repr__(self):
		return f"AltairChart <{str(self.dobj)}>"
	def addTooltip(self):
		if (self.tooltip): 
			self.chart = self.chart.encode(tooltip=list(self.dobj.dataset.df.columns))
	def encodeColor(self):
		colorAttr = self.dobj.getObjFromChannel("color")
		if (len(colorAttr)==1):
			self.chart = self.chart.encode(color=colorAttr[0].columnName)
		elif (len(colorAttr)>1):
			raise ValueError("There should not be more than one attribute specified in the same channel.")
	def addTitle(self):
		chartTitle = self.dobj.title
		if chartTitle:
			self.chart = self.chart.encode().properties(
				title = chartTitle
			)

	def initializeChart(self):
		return NotImplemented