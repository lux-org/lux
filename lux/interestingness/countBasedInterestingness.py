def countBasedInterestingness(dobj):
	import pandas as pd
	from scipy.stats import skew

	dimension = dobj.getObjByDataModel("dimension")[0].columnName
	counts = list(dobj.dataset.df.groupby(dimension).count().iloc[:,0])

	numFilters = len(dobj.getObjByRowColType("Row"))
	if numFilters == 0:
		skewness = skew(msrVals)
		return(skewness)
	else:
		#compare filtered data's distribution to original distribution
