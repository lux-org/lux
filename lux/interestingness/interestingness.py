from lux.executor.PandasExecutor import PandasExecutor
from lux.utils import utils
def interestingness(view,ldf):
	import pandas as pd
	import numpy as np
	from pandas.api.types import is_datetime64_any_dtype as is_datetime


	n_dim = 0
	n_msr = 0
	
	filterSpecs = utils.getFilterSpecs(view.specLst)
	viewAttrsSpecs = utils.getAttrsSpecs(view.specLst)

	for spec in viewAttrsSpecs:
		if (spec.attribute!="Record"):
			if (spec.dataModel == 'dimension'):
				n_dim += 1
			if (spec.dataModel == 'measure'):
				n_msr += 1
	n_filter = len(filterSpecs)
	attr_specs = [spec for spec in viewAttrsSpecs if spec.attribute != "Record"]
	# print (n_filter, n_dim,n_msr)
	# Bar Chart (Count)
	if (n_dim == 1 and n_msr == 0 and n_filter == 0):
		v = ldf[attr_specs[0].attribute].value_counts()
		C = len(v)
		D = (0.5) ** C

		if (is_datetime(v)):
			v = v.astype('int')

		return skewness(D, v)
	elif (n_dim == 1 and n_msr == 0 and n_filter == 1):
		v = ldf[attr_specs[0].attribute].value_counts()
		filter_spec = filterSpecs[0]
		v_filter = PandasExecutor.applyFilter(ldf, filter_spec.attribute, filter_spec.filterOp, filter_spec.value)[attr_specs[0].attribute]
		v_filter = v.filter(items=v_filter.keys())

		if (len(v_filter) < len(v)):
			v_filter = v_filter.append(pd.Series([0] * (len(v) - len(v_filter))))
		sig = len(v_filter)
		return sig * filtered_dist_shape_diff(v, v_filter)
	
	# Histogram (Count)
	elif (n_dim == 0 and n_msr == 1 and n_filter == 0):
		v = ldf[attr_specs[0].attribute]
		
		return agg_value_magnitude(v)
	elif (n_dim == 0 and n_msr == 1 and n_filter == 1):
		v = ldf[attr_specs[0].attribute]
		C = len(v.unique())

		# if c < 40 # c == cardinality (number of unique values)
		if (C >= 40):
			return 0

		filter_spec = filterSpecs[0]
		v_filter = PandasExecutor.applyFilter(ldf, filter_spec.attribute, filter_spec.filterOp, filter_spec.value)[attr_specs[0].attribute]

		if (len(v_filter) < len(v)):
			v_filter = v_filter.append(pd.Series([0] * (len(v) - len(v_filter))))

		v_bin = v
		v_filter_bin = v_filter

		if (filter_spec.binSize > 0):
			v_bin = np.histogram(v, bins=filter_spec.binSize)[0]
			v_filter_bin = np.histogram(v_filter, bins=filter_spec.binSize)[0]
		sig = len(v_filter)
		return sig*filtered_hist_shape_diff(v, v_filter, v_bin, v_filter_bin)

	# Bar Chart
	elif (n_dim == 1 and n_msr == 1 and n_filter == 0):
		if view.data is not None:
			v = view.data[attr_specs[0].attribute]
		else:
			v = ldf[attr_specs[0].attribute]
		C = len(v.unique())
		D = (0.5) ** C
		v_flat = pd.Series([1 / C] * len(v))
		if (is_datetime(v)):
			v = v.astype('int')
		
		return unevenness(D, v, v_flat)
	elif (n_dim == 1 and n_msr == 1 and n_filter == 1):
		#view.data will already be populated if using SQL Executor
		dimension = view.getAttrByDataModel("dimension")[0].attribute
		measure = view.getAttrByDataModel("measure")[0].attribute
		if ldf.executorType == "SQL":
			return(0)
			v = view.data[measure]
		else:
			v = ldf[measure]
		dim = view.data[dimension]
		C = len(dim.unique())

		# if c < 40 # c == cardinality (number of unique values)
		if (C >= 40):
			return 0

		filter_spec = filterSpecs[0]
		v_filter = PandasExecutor.applyFilter(ldf, filter_spec.attribute, filter_spec.filterOp, filter_spec.value)[attr_specs[0].attribute]

		if (len(v_filter) < len(v)):
			v_filter = v_filter.append(pd.Series([0] * (len(v) - len(v_filter))))
			
		v_bin = v
		v_filter_bin = v_filter

		if (filter_spec.binSize > 0):
			v_bin = np.histogram(v, bins=filter_spec.binSize)[0]
			v_filter_bin = np.histogram(v_filter, bins=filter_spec.binSize)[0]
		sig = len(v_filter)
		return sig*deviation(v, v_filter, v_bin, v_filter_bin)

	# Scatter Plot
	elif (n_dim == 0 and n_msr == 2):
		if (n_filter==1):
			filter_spec = filterSpecs[0]
			ldf = PandasExecutor.applyFilter(ldf, filter_spec.attribute, filter_spec.filterOp, filter_spec.value)
			return ldf.size
		v_x = ldf[attr_specs[0].attribute]
		v_y = ldf[attr_specs[1].attribute]
		return monotonicity(v_x, v_y)
	# Scatterplot colored by Dimension
	elif (n_dim == 1 and n_msr == 2):
		colorAttr = view.getAttrByChannel("color")[0].attribute
		
		C = ldf.cardinality[colorAttr]
		if (C<40):
			return 1/C
		else:
			return -1
	# Scatterplot colored by dimension
	elif (n_dim== 1 and n_msr == 2):
		return 0.2
	# Scatterplot colored by measure
	elif (n_msr == 3):
		return 0.1
	# Default
	else:
		return -1


##### Bar Chart (Count) #####

# N_dim = 1, N_msr = 0, N_filter = 0
def skewness(D, v):
	from scipy.stats import skew

	return D * skew(v)

# N_dim = 1, N_msr = 0, N_filter = 1
def filtered_dist_shape_diff(v, v_filter):
	# TODO: Jared

	# Euclidean distance as L2 function
	from scipy.spatial.distance import euclidean

	# Norm for vector magnitude
	from numpy.linalg import norm

	return 0.1 * (norm(v_filter) / norm(v)) * euclidean(v, v_filter)

##############################







##### Histogram (Count) #####

# N_dim = 0, N_msr = 1, N_filter = 0
def agg_value_magnitude(v):
	return sum(v)

# N_dim = 0, N_msr = 1, N_filter = 1
def filtered_hist_shape_diff(v, v_filter):
	# Euclidean distance as L2 function
	from scipy.spatial.distance import euclidean

	# Norm for vector magnitude
	from numpy.linalg import norm

	return (norm(v_filter) / norm(v)) * euclidean(v_bin, v_filter_bin)

##############################








##### Bar Chart #####

# N_dim = 1, N_msr = 1, N_filter = 0
def unevenness(D, v, v_flat):
	# Euclidean distance as L2 function
	from scipy.spatial.distance import euclidean
	
	return D * euclidean(v, v_flat)

# N_dim = 1, N_msr = 1, N_filter = 1
def deviation(v, v_filter, v_bin, v_filter_bin):
	# Euclidean distance as L2 function
	from scipy.spatial.distance import euclidean

	# Norm for vector magnitude
	from numpy.linalg import norm

	return (norm(v_filter) / norm(v)) * euclidean(v, v_filter)

##############################








##### Scatter Plot #####

# N_dim = 0, N_msr = 2, N_filter = 0
def mutual_information(v_x, v_y):
	#Interestingness metric for two measure attributes
  	#Calculate maximal information coefficient (see Murphy pg 61) or Pearson's correlation
	from sklearn.metrics import mutual_info_score

	return mutual_info_score(v_x, v_y)

# N_dim = 0, N_msr = 2, N_filter = 1
def monotonicity(v_x, v_y):
	from scipy.stats import spearmanr
	return (spearmanr(v_x, v_y)[0]) ** 2
	# import scipy.stats
	# return abs(scipy.stats.pearsonr(v_x,v_y)[0])
##############################
