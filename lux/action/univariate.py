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

from lux.interestingness.interestingness import interestingness
from lux.vis.VisList import VisList
import lux
from lux.utils import utils
def univariate(ldf, data_type_constraint="quantitative"):
	'''
	Generates bar chart distributions of different attributes in the dataframe.

	Parameters
	----------
	ldf : lux.core.frame
		LuxDataFrame with underspecified intent.

	data_type_constraint: str
		Controls the type of distribution chart that will be rendered.

	Returns
	-------
	recommendations : Dict[str,obj]
		object with a collection of visualizations that result from the Distribution action.
	'''
	import numpy as np

	filter_specs = utils.get_filter_specs(ldf._intent)
	ignore_rec_flag = False
	if (data_type_constraint== "quantitative"):
		intent = [lux.Clause("?",data_type="quantitative",exclude="Number of Records")]
		intent.extend(filter_specs)
		recommendation = {"action":"Distribution",
						  "description":"Show univariate histograms of <p class='highlight-descriptor'>quantitative</p>  attributes."}
		if (len(ldf)<5): # Doesn't make sense to generate a histogram if there is less than 5 datapoints (pre-aggregated)
			ignore_rec_flag = True
	elif (data_type_constraint == "nominal"):
		intent = [lux.Clause("?",data_type="nominal")]
		intent.extend(filter_specs)
		recommendation = {"action":"Occurrence",
						   "description":"Show frequency of occurrence for <p class='highlight-descriptor'>categorical</p> attributes."}
	elif (data_type_constraint == "temporal"):
		intent = [lux.Clause("?",data_type="temporal")]
		intent.extend(filter_specs)
		recommendation = {"action":"Temporal",
						   "description":"Show trends over <p class='highlight-descriptor'>time-related</p> attributes."}
		if (len(ldf)<3): # Doesn't make sense to generate a line chart if there is less than 3 datapoints (pre-aggregated)
			ignore_rec_flag = True
	if (ignore_rec_flag):
		recommendation["collection"] = []
		return recommendation
	vlist = VisList(intent,ldf)
	for vis in vlist:
		vis.score = interestingness(vis,ldf)
	# vlist = vlist.topK(15) # Basic visualizations should not be capped
	vlist.sort()
	recommendation["collection"] = vlist
	return recommendation