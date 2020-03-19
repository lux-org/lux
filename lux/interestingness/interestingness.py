from lux.interestingness.valueBasedInterestingness import valueBasedInterestingness
from lux.interestingness.relationshipBasedInterestingness import relationshipBasedInterestingness
def interestingness(view,ldf):
	# TODO: add back if (ldf.dataset.cardinality[cVar]>10): then score -1 for categorical values
	numAttrs = len(view.getAttrsSpecs())
	if numAttrs == 1:
		attrType = view.specLst[0].dataModel
		if attrType == "measure":
			return(valueBasedInterestingness(view,ldf))
		elif attrType == "dimension":
			return(0.5)
			#from interestingness import countBasedInterestingness
			#return(countBasedinterstingness(dobjCompiled))
	elif numAttrs == 2:
		numMeasure = len(view.getObjByDataModel("measure"))
		numDimension = len(view.getObjByDataModel("dimension"))

		if numMeasure == 2:
			return(relationshipBasedInterestingness(view,ldf))
		elif numMeasure == 1 and numDimension == 1:
			return(0.5)
			#from interstingness import distributionBasedInterestingness
			#return(distributionBasedInterestingness(dobjCompiled))
		else:
			return(0)
	else:
		return(0.5)