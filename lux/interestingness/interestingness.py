from lux.interestingness.valueBasedInterestingness import valueBasedInterestingness
from lux.interestingness.relationshipBasedInterestingness import relationshipBasedInterestingness
def interestingness(dobj):
	dobjCompiled = dobj.compiled
	numAttributes = len(dobj.getObjByRowColType("Column"))
	if numAttributes == 1:
		attrType = dobjCompiled.spec[0].dataModel
		if attrType == "measure":
			return(valueBasedInterestingness(dobjCompiled))
		elif attrType == "dimension":
			return(0.5)
			#from interestingness import countBasedInterestingness
			#return(countBasedinterstingness(dobjCompiled))
	elif numAttributes == 2:
		numMeasure = len(dobjCompiled.getObjByDataModel("measure"))
		numDimension = len(dobjCompiled.getObjByDataModel("dimension"))

		if numMeasure == 2:
			return(relationshipBasedInterestingness(dobjCompiled))
		elif numMeasure == 1 and numDimension == 1:
			return(0.5)
			#from interstingness import distributionBasedInterestingness
			#return(distributionBasedInterestingness(dobjCompiled))
		else:
			return(0)
	else:
		return(0.5)