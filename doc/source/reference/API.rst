.. _API:

****
API
****

Core Lux Objects
-----------------

.. autosummary::
	:toctree: gen
	:nosignatures:

	lux.core.frame.LuxDataFrame
	lux.core.series.LuxSeries

Configuration Options
----------------------

.. autosummary::
	:toctree: gen
	:nosignatures:

	lux._config.config.Config

Basic API Interface
-------------------

.. autosummary::
	:toctree: gen
	:nosignatures: 

	lux.vis.Vis.Vis
	lux.vis.VisList.VisList
	lux.vis.Vis.Clause

Advanced Internals (Dev)
-------------------------

.. autosummary::
	:toctree: gen
	:nosignatures: 
	
	lux.processor.Compiler.Compiler
	lux.processor.Parser.Parser
	lux.processor.Validator.Validator
	lux.executor.Executor.Executor
	lux.executor.PandasExecutor.PandasExecutor
	lux.executor.SQLExecutor.SQLExecutor
	lux.vislib.altair.AltairChart.AltairChart
	lux.vislib.altair.AltairRenderer.AltairRenderer
	lux.vislib.altair.BarChart.BarChart
	lux.vislib.altair.Histogram.Histogram
	lux.vislib.altair.LineChart.LineChart
	lux.vislib.altair.ScatterChart.ScatterChart
