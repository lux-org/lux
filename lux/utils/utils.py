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

def convert_to_list(x):
	'''
	"a" --> ["a"]
	["a","b"] --> ["a","b"]
	'''
	if type(x) != list:
		return [x]
	else:
		return x

def pandas_to_lux(df):
	from lux.core.frame import LuxDataFrame
	values = df.values.tolist()
	ldf = LuxDataFrame(values, columns = df.columns)
	return(ldf)

def get_attrs_specs(intent):
	if (intent is None): return []
	spec_obj = list(filter(lambda x: x.value=="", intent))
	return spec_obj

def get_filter_specs(intent):
	if (intent is None): return []
	spec_obj = list(filter(lambda x: x.value!="", intent))
	return spec_obj

def check_import_lux_widget():
	import pkgutil
	if (pkgutil.find_loader("luxWidget") is None):
		raise Exception("luxWidget is not installed. Run `npm i lux-widget' to install the Jupyter widget.\nSee more at: https://github.com/lux-org/lux-widget")

def get_agg_title(clause):
	if (clause.aggregation is None):
		return f'{clause.attribute}'
	elif (clause.attribute=="Record"):
		return f'Number of Records'
	else:
		return f'{clause._aggregation_name.capitalize()} of {clause.attribute}'
def check_if_id_like(df,attribute):
	import re
	# Strong signals
	high_cardinality = df.cardinality[attribute]>500 # so that aggregated reset_index fields don't get misclassified
	attribute_contain_id = re.search(r'id',attribute) is not None
	almost_all_vals_unique = df.cardinality[attribute] >=0.98* len(df)
	# TODO: Could probably add some type of entropy measure (since the binned id fields are usually very even)
	return high_cardinality and (attribute_contain_id or almost_all_vals_unique)