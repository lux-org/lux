'''
Gets a measure of skewness of the distributions of all measures
'''
from lux.interestingness.interestingness import interestingness
import lux
from lux.executor.PandasExecutor import PandasExecutor
def distribution(ldf,dataTypeConstraint="quantitative"):
	import scipy.stats
	import numpy as np
	if (dataTypeConstraint=="quantitative"):
		ldf.setContext([lux.Spec("?",dataType="quantitative")])
		recommendation = {"action":"Distribution",
							"description":"Show univariate count distributions of different attributes in the dataset."}
	elif (dataTypeConstraint=="nominal"):
		ldf.setContext([lux.Spec("?",dataType="nominal")])
		recommendation = {"action":"Category",
						   "description":"Show bar chart distributions of different attributes in the dataset."}

	vc = ldf.viewCollection
	PandasExecutor.execute(vc,ldf)
	for view in vc:
		view.score = interestingness(view,ldf)

	vc.sort()
	ldf.clearContext()
	recommendation["collection"] = vc
	# dobj.recommendations.append(recommendation)
	return recommendation