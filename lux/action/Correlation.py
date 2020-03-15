import lux
from lux.interestingness.interestingness import interestingness
from lux.compiler.Compiler import Compiler
from lux.executor.ExecutionEngine import ExecutionEngine

# change ignoreTranspose to false for now.
def correlation(ldf,ignoreIdentity=True,ignoreTranspose=False):
	import scipy.stats
	import numpy as np

	recommendation = {"action":"Correlation",
						   "description":"Show relationships between two quantitative variables."}
	vc = ldf.viewCollection
	# if (ignoreIdentity): vc = filter(lambda x: x.specLst[0].attribute!=x.specLst[1].attribute,ldf.viewCollection)
	vc = Compiler.compile(ldf, vc, enumerateCollection=False)

	ExecutionEngine.execute(vc,ldf)
	# Then use the data populated in the view collection to compute score
	for view in vc:
		measures = view.getObjByDataModel("measure")
		if len(measures)<2 : raise ValueError(f"Can not compute correlation between {[x.attribute for x in ldf.columns]} since less than 2 measure values present.")
		msr1 = measures[0].attribute
		msr2 = measures[1].attribute

		msr1Vals = list(ldf[msr1])
		msr2Vals = list(ldf[msr2])

		if (ignoreTranspose):
			# print(msr1,msr2)
			checkTranspose = checkTransposeNotComputed(ldf,msr1,msr2)
		else:
			checkTranspose = True
		if (checkTranspose):
			view.score = np.abs(scipy.stats.pearsonr(msr1Vals,msr2Vals)[0])
		else:
			view.score = -1
	vc.sort(removeInvalid=True)
	recommendation["collection"] = vc
	return recommendation

def checkTransposeNotComputed(ldf,a,b):
	# how to know if these are just columns?
	transposeExist = list(filter(lambda x:(x.specLst[0].attribute==b) and (x.specLst[1].attribute==a),ldf.viewCollection)) # Jaywoo
	if (len(transposeExist)>0):
		return transposeExist[0].score==-1
	else:
		return False