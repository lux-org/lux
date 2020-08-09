from sklearn.metrics import mutual_info_score
import numpy as np
from math import sqrt
def mutualInformationScore(measures, data):
	m1Val = data[measures[0]]
	m2Val = data[measures[1]]

	#estimate mutual information using histograms with a default number of bins
	bins = sqrt(len(data)/5)
	c_xy = np.histogram2d(m1Val, m2Val, bins)[0]
	mi = mutual_info_score(None, None, contingency=c_xy)
	return(mi)