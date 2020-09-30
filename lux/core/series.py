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