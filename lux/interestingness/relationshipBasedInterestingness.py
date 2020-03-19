def relationshipBasedInterestingness(view,ldf):
	from scipy.stats import pearsonr

	#Interestingness metric for two measure attributes
  	#Calculate maximal information coefficient (see Murphy pg 61) or Pearson's correlation
	measures = view.getObjByDataModel("measure")
	m1 = measures[0].columnName
	m2 = measures[1].columnName

	if len(view.getFilterSpecs()) == 0:
		from sklearn.metrics import mutual_info_score
		import numpy as np
		from math import sqrt

		m1Val = ldf[m1]
		m2Val = ldf[m2]

		#estimate mutual information using histograms with a default number of bins
		bins = sqrt(len(ldf)/5)
		c_xy = np.histogram2d(m1Val, m2Val, bins)[0]
		mi = mutual_info_score(None, None, contingency=c_xy)
		return(mi)

	else:
		row = view.getFilterSpecs()[0]
		filteredData = ldf[ldf[row.fAttribute] == row.fVal]
		if len(filteredData) > 20: # should have at least 20 datapoints to compute a correlation
			m1Val = filteredData[m1]
			m2Val = filteredData[m2]
			pearsonCorr = pearsonr(m1Val, m2Val)[0]
			return(pearsonCorr)
		else:
			return(-1)