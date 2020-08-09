from scipy.stats import pearsonr
def filteredCorrelationScore(measures, data, filterVar = "", filterVal = ""):
	filteredData = data[data[filterVar] == filterVal]
	if len(filteredData) > 20: # should have at least 20 datapoints to compute a correlation
		m1Val = filteredData[measures[0]]
		m2Val = filteredData[measures[1]]
		pearsonCorr = pearsonr(m1Val, m2Val)[0]
		return(pearsonCorr)
	else:
		return(-1)