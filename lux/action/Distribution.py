'''
Gets a measure of skewness of the distributions of all measures
'''
from lux.interestingness.interestingness import interestingness
import lux
from lux.executor.PandasExecutor import PandasExecutor
def distribution(ldf):
	# Enumerate --> compute the scores for each item in the collection
	# -->  return DataObjectCollection with the scores
	import scipy.stats
	import numpy as np
	recommendation = {"action":"Distribution",
						   "description":"Show univariate count distributions of different attributes in the dataset."}
	vc = ldf.viewCollection
	PandasExecutor.execute(vc,ldf)
	for view in vc:
		# measure = obj.getObjByDataModel("measure")[0]
		# msr = measure.columnName
		fieldName = list(filter(lambda x: x.attribute!="count()", view.specLst))[0].attribute
		fieldVals = list(ldf[fieldName])
		if (ldf.dataModelLookup[fieldName]=="measure"):
			# view.score = np.abs(scipy.stats.skew(fieldVals))
			# view.score = 0.5
			view.score = interestingness(view,ldf)
		else: # TODO: this should be based on interestingness (i.e, deviation case)
			# obj.score = interestingness(obj)
			view.score = interestingness(view,ldf)

	vc.sort()
	recommendation["collection"] = vc
	# dobj.recommendations.append(recommendation)
	return recommendation