import lux
import pandas as pd
from typing import Callable
from lux.vizLib.altair.BarChart import BarChart
from lux.vizLib.altair.ScatterChart import ScatterChart
from lux.vizLib.altair.LineChart import LineChart
from lux.vizLib.altair.Histogram import Histogram

class AltairRenderer:
	"""
	Renderer for Charts based on Altair (https://altair-viz.github.io/)
	"""
	def __init__(self,outputType="VegaLite"):
		self.outputType = outputType
	def __repr__(self):
		return f"AltairRenderer"
	def createVis(self,view):
		"""
		Input DataObject and return a visualization specification
		
		Parameters
		----------
		view: lux.view.View
			Input View (with data)
		
		Returns
		-------
		chart : altair.Chart
			Output Altair Chart Object
		"""	
		# If a column has a Period dtype, or contains Period objects, convert it back to Datetime
		for attr in list(view.data.columns):
			if pd.api.types.is_period_dtype(view.data.dtypes[attr]) or isinstance(view.data[attr].iloc[0], pd.Period):
				dateColumn = view.data[attr]
				view.data[attr] = pd.PeriodIndex(dateColumn.values).to_timestamp()
		
		if (view.mark =="histogram"):
			chart = Histogram(view)
		elif (view.mark =="bar"):
			chart = BarChart(view)
		elif (view.mark =="scatter"):
			chart = ScatterChart(view)
		elif (view.mark =="line"):
			chart = LineChart(view)
		else:
			chart = None

		if (chart):
			if (self.outputType=="VegaLite"):
				if (view.plotConfig): chart.chart = view.plotConfig(chart.chart)
				chartDict = chart.chart.to_dict()
				# this is a bit of a work around because altair must take a pandas dataframe and we can only generate a luxDataFrame
				# chart["data"] =  { "values": view.data.to_dict(orient='records') }
				chartDict["width"] = 160
				chartDict["height"] = 150
				return chartDict
			elif (self.outputType=="Altair"):
				import inspect
				if (view.plotConfig): chart.code +='\n'.join(inspect.getsource(view.plotConfig).split('\n    ')[1:-1])
				chart.code +="\nchart"
				chart.code = chart.code.replace('\n\t\t','\n')
				return chart.code