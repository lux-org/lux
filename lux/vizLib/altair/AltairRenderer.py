import lux
from lux.vizLib.altair.BarChart import BarChart
from lux.vizLib.altair.ScatterChart import ScatterChart
from lux.vizLib.altair.LineChart import LineChart
from lux.vizLib.altair.Histogram import Histogram

class AltairRenderer:
	"""
	Renderer for Altair Charts
	"""
	def __init__(self):
		pass
	def __repr__(self):
		return f"AltairRenderer"
	def createVis(self,dobj):
		"""
		Input DataObject and return a visualization specification
		
		Parameters
		----------
		dobj : lux.DataObj
			Input DataObject
		
		Returns
		-------
		chart : altair.Chart
			Output Altair Chart Object
		"""		
		if (dobj.mark =="histogram"):
			chart = Histogram(dobj)
		elif (dobj.mark =="bar"):
			chart = BarChart(dobj)
		elif (dobj.mark =="scatter"):
			chart = ScatterChart(dobj)
		elif (dobj.mark =="line"):
			chart = LineChart(dobj)
		chart = chart.chart.to_dict()
		# del chart["datasets"]
		# chart["data"] =  { "name": 'chartData' }
		chart["width"] = 160
		chart["height"] = 150
		return chart