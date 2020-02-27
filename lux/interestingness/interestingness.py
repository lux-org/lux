from lux.interestingness.skewScore import skewScore
from lux.interestingness.kurtosisScore import kurtosisScore
from lux.interestingness.peakScore import *
def interestingness(measures, dimensions, data, filterVar="", filterVal=""):
	numAttributes = len(measures) + len(dimensions)
	if numAttributes == 1:
		if len(measures) == 1
			return(skewScore(measures[0],data))
		elif attrType == "dimension":
			return(0.5)
			#from interestingness import countBasedInterestingness
			#return(countBasedinterstingness(dobjCompiled))
	elif numAttributes == 2:
		if len(measures) == 2:
			return(mutualInformationScore(measures, data))
		elif numMeasure == 1 and numDimension == 1:
			return(0.5)
			#from interstingness import distributionBasedInterestingness
			#return(distributionBasedInterestingness(dobjCompiled))
		else:
			return(0)
	else:
		return(0.5)