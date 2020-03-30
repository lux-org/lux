from lux.interestingness.valueBasedInterestingness import valueBasedInterestingness
from lux.interestingness.relationshipBasedInterestingness import relationshipBasedInterestingness

def interestingness(view,ldf):
	# print()
	# print(view)
	# print(view.getAttrsSpecs())
	# # TODO: add back if (ldf.dataset.cardinality[cVar]>10): then score -1 for categorical values
	# numAttrs = len(view.getAttrsSpecs())
	# if numAttrs == 1:
	# 	attrType = view.specLst[0].dataModel
	# 	if attrType == "measure":
	# 		return(valueBasedInterestingness(view,ldf))
	# 	elif attrType == "dimension":
	# 		return(0.5)
	# 		#from interestingness import countBasedInterestingness
	# 		#return(countBasedinterstingness(dobjCompiled))
	# elif numAttrs == 2:
	# 	numMeasure = len(view.getObjByDataModel("measure"))
	# 	numDimension = len(view.getObjByDataModel("dimension"))

	# 	if numMeasure == 2:
	# 		return(relationshipBasedInterestingness(view,ldf))
	# 	elif numMeasure == 1 and numDimension == 1:
	# 		return(0.5)
	# 		#from interstingness import distributionBasedInterestingness
	# 		#return(distributionBasedInterestingness(dobjCompiled))
	# 	else:
	# 		return(0)
	# else:
	# 	return(0.5)




	# n_dim = len(view.getObjByDataModel('dimension'))
	# n_msr = len(view.getObjByDataModel('measure'))
	n_dim = 0
	n_msr = 0
	for spec in view.specLst:
		if (spec.attribute):
			if (spec.dataModel == 'dimension'):
				n_dim += 1
			if (spec.dataModel == 'measure'):
				n_msr += 1
	n_filter = len(view.getFilterSpecs())

	print(n_dim, n_msr, n_filter)
	

	# Some other testing I'm doing
	
	# print(ldf[view.spec[0].attribute].sum(skipna = True))
	# print(view.getAttrsSpecs()[0].attribute)
	# print(view.getAttrsSpecs())
	# print([x.attribute for x in view.getAttrsSpecs()])
	# return 0.5


	# Bar Chart (Count)
	if (n_dim == 1 and n_msr == 0 and n_filter == 0):
		return 0.5
		# return skewness()
	elif (n_dim == 1 and n_msr == 0 and n_filter == 1):
		return 0.5
		# return filtered_dist_shape_diff()
	
	# Histogram (Count)
	elif (n_dim == 0 and n_msr == 1 and n_filter == 0):
		return 0.5
		# return agg_value_magnitude()
	elif (n_dim == 0 and n_msr == 1 and n_filter == 1):
		return 0.5
		# return filtered_hist_shape_diff()

	# Bar Chart
	elif (n_dim == 1 and n_msr == 1 and n_filter == 0):
		return 0.5
		# return unevenness()
	elif (n_dim == 1 and n_msr == 1 and n_filter == 1):
		return 0.5
		# if c < 40 # c == cardinality (number of unique values)
		# return deviation()

	# Scatter Plot
	elif (n_dim == 0 and n_msr == 2 and n_filter == 0):
		return 0.5
		# return mutual_information()
	elif (n_dim == 0 and n_msr == 2 and n_filter == 1):
		return 0.5
		# return monotonicity()

	# Default
	else:
		return 0.5







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
	from np.linalg import norm

	# return 0.1 * (norm(v_filter) / norm(v)) * euclidean(v, v_filter)
	return 0.5

##############################







##### Histogram (Count) #####

# N_dim = 0, N_msr = 1, N_filter = 0
def agg_value_magnitude(v):
	return sum(v)

# N_dim = 0, N_msr = 1, N_filter = 1
def filtered_hist_shape_diff(v, v_filter):
	# TODO: Jared

	# Euclidean distance as L2 function
	from scipy.spatial.distance import euclidean

	# Norm for vector magnitude
	from np.linalg import norm

	# return (norm(v_filter) / norm(v)) * euclidean(BIN?? v, BIN?? v_filter)
	return 0.5

##############################








##### Bar Chart #####

# N_dim = 1, N_msr = 1, N_filter = 0
def unevenness(D, v, v_flat):
	# TODO: Jared
	# Euclidean distance as L2 function
	from scipy.spatial.distance import euclidean
	
	# return D * euclidean(v, v_flat)
	return 0.5

# N_dim = 1, N_msr = 1, N_filter = 1
def deviation(v, v_filter):
	# TODO: Jared

	# Euclidean distance as L2 function
	from scipy.spatial.distance import euclidean

	# Norm for vector magnitude
	from np.linalg import norm

	# return (norm(v_filter) / norm(v)) * euclidean(BIN????? v, BIN?????? v_filter)
	return 0.5

##############################








##### Scatter Plot #####

# N_dim = 0, N_msr = 2, N_filter = 0
def mutual_information(v_x, v_y):
	# TODO: Jared
	from sklearn.metrics import mutual_info_score

	# return mutual_info_score(v_x, v_y)
	return 0.5

# N_dim = 0, N_msr = 2, N_filter = 1
def monotonicity(v_x, v_y):
	# TODO: Jared
	from scipy.stats import spearmanr

	# return (spearmanr(v_x, v_y)[0]) ** 2
	return 0.5

##############################
