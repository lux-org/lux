import pandas as pd
class LuxSeries(pd.Series):
	# _metadata =  ['name','_intent','data_type_lookup','data_type',
	# 			 'data_model_lookup','data_model','unique_values','cardinality',
	# 			'min_max','plot_config', '_current_vis','_widget', '_recommendation']
	def __init__(self,*args, **kw):
		super(LuxSeries, self).__init__(*args, **kw)
	@property
	def _constructor(self):
		return LuxSeries

	@property
	def _constructor_expanddim(self):
		from lux.core.frame import LuxDataFrame
		# def f(*args, **kwargs):
		# 	# adapted from https://github.com/pandas-dev/pandas/issues/13208#issuecomment-326556232
		# 	return LuxDataFrame(*args, **kwargs).__finalize__(self, method='inherit')
		# return f
		return LuxDataFrame