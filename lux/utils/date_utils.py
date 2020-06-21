import pandas as pd

def dateFormatter(timeStamp,ldf):
	"""
	Given a numpy timestamp and ldf, inspects which date granularity is appropriate and reformats timestamp accordingly

	Example
	----------
	For changing granularity the results differ as so.
	days: '2020-01-01' -> '2020-1-1'
	months: '2020-01-01' -> '2020-1'
	years: '2020-01-01' -> '2020'

	Parameters
	----------
	timeStamp: np.datetime64 
		timestamp object holding the date information
	ldf : lux.luxDataFrame.LuxDataFrame
		LuxDataFrame with a temporal field

	Returns
	-------
	dateStr: str
		A reformatted version of the timeStamp according to granularity
	"""
	datetime = pd.to_datetime(timeStamp)
	granularity = computeDateGranularity(ldf)
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
	"""
	Given a ldf, inspects temporal column and finds out the granularity of dates.

	Example
	----------
	['2018-01-01', '2019-01-02', '2018-01-03'] -> "day"
	['2018-01-01', '2019-02-01', '2018-03-01'] -> "month"
	['2018-01-01', '2019-01-01', '2020-01-01'] -> "year"

	Parameters
	----------
	ldf : lux.luxDataFrame.LuxDataFrame
		LuxDataFrame with a temporal field

	Returns
	-------
	field: str
		A str specifying the granularity of dates for the inspected temporal column
	"""
	dateFields = ["day", "month", "year"]
	if ldf.dataType["temporal"]:
		dateColumn = ldf[ldf.dataType["temporal"][0]] # assumes only one temporal column, may need to change this function to recieve multiple temporal columns in the future
		dateIndex = pd.DatetimeIndex(dateColumn)
		for field in dateFields:
			if hasattr(dateIndex,field) and len(getattr(dateIndex, field).unique()) != 1 : #can be changed to sum(getattr(dateIndex, field)) != 0
				return field
