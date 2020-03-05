'''
Correlation between measure variables
'''
import lux
# def correlation(dobj,ignoreIdentity=True,ignoreTranspose=True):
# 	# Enumerate --> compute the scores for each item in the collection
# 	# -->  return DataObjectCollection with the scores
# 	import scipy.stats
# 	import numpy as np
# 	# TODO: need to make this work for DataObject (when input is not collection and just a single DataObject)
# 	result = lux.Result()
# 	recommendation = {"action":"Correlation",
# 						   "description":"Show relationships between two quantitative variables."}
# 	vizCollection = dobj.compiled.collection
# 	if (ignoreIdentity): vizCollection =  filter(lambda x: x.spec[0].columnName!=x.spec[1].columnName,dobj.compiled.collection)
# 	def checkTransposeNotComputed(dobj,a,b):
# 		transposeExist = list(filter(lambda x:(x.spec[0].columnName==b) and (x.spec[1].columnName==a),dobj.compiled.collection))
# 		if (len(transposeExist)>0):
# 			return transposeExist[0].score==-1
# 		else:
# 			return False
# 	for obj in vizCollection:
# 		measures = obj.getObjByDataModel("measure")
# 		if len(measures)<2 : raise ValueError(f"Can not compute correlation between {[x.columnName for x in obj.spec]} since less than 2 measure values present.")
# 		msr1 = measures[0].columnName
# 		msr2 = measures[1].columnName
#
# 		msr1Vals = list(obj.dataset.df[msr1])
# 		msr2Vals = list(obj.dataset.df[msr2])
#
# 		if (ignoreTranspose):
# 			checkTranspose = checkTransposeNotComputed(dobj,msr1,msr2)
# 		else:
# 			checkTranspose = True
# 		if (checkTranspose):
# 			obj.score = np.abs(scipy.stats.pearsonr(msr1Vals,msr2Vals)[0])
# 		else:
# 			obj.score = -1
# 	dobj.compiled.sort(removeInvalid=True)
# 	recommendation["collection"] = dobj.compiled
# 	# dobj.recommendations.append(recommendation)
# 	result.addResult(recommendation,dobj)
# 	return result


import lux
def correlation(ldf, ignoreIdentity=True, ignoreTranspose=True):
	# Enumerate --> compute the scores for each item in the collection
	# -->  return DataObjectCollection with the scores
	import scipy.stats
	import numpy as np
	# TODO: need to make this work for DataObject (when input is not collection and just a single DataObject)
	result = lux.Result()
	recommendation = {"action": "Correlation",
					  "description": "Show relationships between two quantitative variables."}

	vizCollection = ldf.viewCollection

	if (ignoreIdentity): vizCollection = filter(lambda x: x.spec[0].attribute != x.spec[1].attribute,
												ldf.viewCollection)

	def checkTransposeNotComputed(ldf, a, b):
		transposeExist = list(
			filter(lambda x: (x.spec[0].attribute == b) and (x.spec[1].attribute == a), ldf.viewCollection))
		if (len(transposeExist) > 0):
			return transposeExist[0].score == -1
		else:
			return False

	for view in vizCollection:
		measures = view.getObjByDataModel("measure")
		if len(measures) < 2: raise ValueError(
			f"Can not compute correlation between {[x.columnName for x in view.spec]} since less than 2 measure values present.")
		msr1 = measures[0].attribute
		msr2 = measures[1].attribute

		msr1Vals = list(view.data[msr1])
		msr2Vals = list(view.data[msr2])

		if (ignoreTranspose):
			checkTranspose = checkTransposeNotComputed(ldf, msr1, msr2)
		else:
			checkTranspose = True
		if (checkTranspose):
			view.score = np.abs(scipy.stats.pearsonr(msr1Vals, msr2Vals)[0])
		else:
			view.score = -1
	ldf.viewCollection.sort(removeInvalid=True)
	recommendation["collection"] = ldf.viewCollection
	result.addResult(recommendation, ldf)
	return result