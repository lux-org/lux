import pandas as pd

def convert2List(x):
	'''
	"a" --> ["a"]
	["a","b"] --> ["a","b"]
	'''
	if type(x) != list:
		return [x]
	else:
		return x

def pandasToLux(df):
	from lux.luxDataFrame.LuxDataframe import LuxDataFrame
	values = df.values.tolist()
	ldf = LuxDataFrame(values, columns = df.columns)
	return(ldf)

def getAttrsSpecs(specLst):
	specObj = list(filter(lambda x: x.value=="", specLst))
	return specObj

def getFilterSpecs(specLst):
	specObj = list(filter(lambda x: x.value!="", specLst))
	return specObj

def checkImportLuxWidget():
	import pkgutil
	if (pkgutil.find_loader("luxWidget") is None):
		raise Exception("luxWidget is not installed. Run `npm i lux-widget' to install the Jupyter widget.\nSee more at: https://github.com/lux-org/lux-widget")

def dateFormatter(timeStamp,ldf):
	datetime = pd.to_datetime(timeStamp)
	if ldf.dateGranularity == "":
		computeDateGranularity(ldf)
	granularity = ldf.dateGranularity
	dateStr = ""
	if granularity == "year":
		dateStr += str(datetime.year)
	elif granularity == "month":
		dateStr += str(datetime.year)+ "-" + str(datetime.month)
	elif granularity == "day":
		dateStr += str(datetime.year) +"-"+ str(datetime.month) +"-"+ str(datetime.day)
	else:
		# non supported granularity
		return datetime.date()

	return dateStr


def computeDateGranularity(ldf):
	dateFields = ["day", "month", "year"]
	if ldf.dataType["temporal"]:
		dateColumn = ldf[ldf.dataType["temporal"][0]]
		dateIndex = pd.DatetimeIndex(dateColumn)
		for idx, field in enumerate(dateFields):
			if len(getattr(dateIndex, field).unique()) != 1 : #can be changed to sum(getattr(dateIndex, field)) != 0
				ldf.dateGranularity = field
				break

