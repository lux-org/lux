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
	from lux.luxDataFrame.LuxDataframe import LuxDataFrame
	values = df.values.tolist()
	ldf = LuxDataFrame(values, columns = df.columns)
	return(ldf)

def get_attrs_specs(spec_lst):
	spec_obj = list(filter(lambda x: x.value=="", spec_lst))
	return spec_obj

def get_filter_specs(spec_lst):
	spec_obj = list(filter(lambda x: x.value!="", spec_lst))
	return spec_obj

def check_import_lux_widget():
	import pkgutil
	if (pkgutil.find_loader("luxWidget") is None):
		raise Exception("luxWidget is not installed. Run `npm i lux-widget' to install the Jupyter widget.\nSee more at: https://github.com/lux-org/lux-widget")


