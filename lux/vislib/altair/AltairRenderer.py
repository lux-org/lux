import lux
import pandas as pd
from typing import Callable
from lux.vislib.altair.BarChart import BarChart
from lux.vislib.altair.ScatterChart import ScatterChart
from lux.vislib.altair.LineChart import LineChart
from lux.vislib.altair.Histogram import Histogram

class AltairRenderer:
	"""
	Renderer for Charts based on Altair (https://altair-viz.github.io/)
	"""
	def __init__(self,output_type="VegaLite"):
		self.output_type = output_type
	def __repr__(self):
		return f"AltairRenderer"
	def create_vis(self,view, standalone=True):
		"""
		Input DataObject and return a visualization specification
		
		Parameters
		----------
		view: lux.vis.Vis
			Input Vis (with data)
		standalone: bool
			Flag to determine if outputted code uses user-defined variable names or can be run independently
		Returns
		-------
		chart : altair.Chart
			Output Altair Chart Object
		"""	
		# If a column has a Period dtype, or contains Period objects, convert it back to Datetime
		if view.data is not None:
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
			if (self.output_type=="VegaLite"):
				if (view.plot_config): chart.chart = view.plot_config(chart.chart)
				chart_dict = chart.chart.to_dict()
				# this is a bit of a work around because altair must take a pandas dataframe and we can only generate a luxDataFrame
				# chart["data"] =  { "values": view.data.to_dict(orient='records') }
				# chart_dict["width"] = 160
				# chart_dict["height"] = 150
				return chart_dict
			elif (self.output_type=="Altair"):
				import inspect
				if (view.plot_config): chart.code +='\n'.join(inspect.getsource(view.plot_config).split('\n    ')[1:-1])
				chart.code +="\nchart"
				chart.code = chart.code.replace('\n\t\t','\n')

				var = view._source
				if var:
					all_vars = []
					for f_info in inspect.getouterframes(inspect.currentframe()):
						local_vars = f_info.frame.f_back
						if local_vars:
							callers_local_vars = local_vars.f_locals.items()
							possible_vars =  [var_name for var_name, var_val in callers_local_vars if var_val is var]
							all_vars.extend(possible_vars)
					found_variable = [possible_var for possible_var in all_vars if possible_var[0] != '_'][0]
				else: # if vis._source was not set when the Vis was created
					found_variable = "df"
				if standalone:
					chart.code = chart.code.replace("placeholder_variable", f"pd.DataFrame({str(view.data.to_dict())})")
				else:
					chart.code = chart.code.replace("placeholder_variable", found_variable) # TODO: Placeholder (need to read dynamically via locals())
				return chart.code