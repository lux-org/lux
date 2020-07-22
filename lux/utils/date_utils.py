import pandas as pd

def date_formatter(time_stamp,ldf):
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
	time_stamp: np.datetime64 
		timestamp object holding the date information
	ldf : lux.luxDataFrame.LuxDataFrame
		LuxDataFrame with a temporal field

	Returns
	-------
	date_str: str
		A reformatted version of the time_stamp according to granularity
	"""
	datetime = pd.to_datetime(time_stamp)
	if ldf.data_type["temporal"]:
		date_column = ldf[ldf.data_type["temporal"][0]] # assumes only one temporal column, may need to change this function to recieve multiple temporal columns in the future
	granularity = compute_date_granularity(date_column)
	date_str = ""
	if granularity == "year":
		date_str += str(datetime.year)
	elif granularity == "month":
		date_str += str(datetime.year)+ "-" + str(datetime.month)
	elif granularity == "day":
		date_str += str(datetime.year) +"-"+ str(datetime.month) +"-"+ str(datetime.day)
	else:
		# non supported granularity
		return datetime.date()

	return date_str


def compute_date_granularity(date_column:pd.core.series.Series):
	"""
	Given a temporal column (pandas.core.series.Series), finds out the granularity of dates.

	Example
	----------
	['2018-01-01', '2019-01-02', '2018-01-03'] -> "day"
	['2018-01-01', '2019-02-01', '2018-03-01'] -> "month"
	['2018-01-01', '2019-01-01', '2020-01-01'] -> "year"

	Parameters
	----------
	date_column: pandas.core.series.Series
		Column series with datetime type

	Returns
	-------
	field: str
		A str specifying the granularity of dates for the inspected temporal column
	"""
	date_fields = ["day", "month", "year"] #supporting a limited set of Vega-Lite TimeUnit (https://vega.github.io/vega-lite/docs/timeunit.html)
	date_index = pd.DatetimeIndex(date_column)
	for field in date_fields:
		if hasattr(date_index,field) and len(getattr(date_index, field).unique()) != 1 : #can be changed to sum(getattr(date_index, field)) != 0
			return field
