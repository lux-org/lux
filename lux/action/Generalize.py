# import lux
# from lux.interestingness.valueBasedInterestingness import valueBasedInterestingness
# # from compiler.Compiler import Compiler
# '''
# Shows possible visualizations when one attribute or filter from the current context is removed
# '''
# def generalize(dobj):
# 	# takes in a dataObject and generates a list of new dataObjects, each with a single measure from the original object removed
# 	# -->  return list of dataObjects with corresponding interestingness scores
# 	import scipy.stats
# 	import numpy as np
# 	result = lux.Result()
# 	recommendation = {"action":"Generalize",
# 						   "description":"Remove one attribute or filter to observe a more general trend."}
# 	output = []
# 	excludedColumns = []
# 	for i in range(0,len(dobj.spec)):
# 		if dobj.spec[i].className == "Column":
# 			columns = dobj.spec[i].columnName
# 			#have to split into two cases, if there is only a single variable in a Column, then its
# 			#columnName value will be a string instead of a list and needs to be handled differently
# 			if type(columns) == list:
# 				for column in columns:
# 					if column not in excludedColumns:
# 						tempDataObj = lux.DataObj(dobj.dataset, dobj.spec)
# 						tempDataObj.removeColumnFromSpecNew(column)
# 						excludedColumns.append(column)
# 						tempDataObj.score = 0.5#valueBasedInterestingness(tempDataObj)
# 						output.append(tempDataObj)
# 			elif type(columns) == str:
# 				if columns not in excludedColumns:
# 					tempDataObj = lux.DataObj(dobj.dataset, dobj.spec)
# 					tempDataObj.removeColumnFromSpecNew(columns)
# 					excludedColumns.append(columns)
# 					tempDataObj.score = 0.5#valueBasedInterestingness(tempDataObj)
# 		elif dobj.spec[i].className == "Row":
# 			newSpec = dobj.spec.copy()
# 			newSpec.pop(i)
# 			tempDataObj = lux.DataObj(dobj.dataset, newSpec)
# 			tempDataObj.score = 0.5#valueBasedInterestingness(tempDataObj)
# 		tempDataObj.compile() # need to recompile
# 		# compiler = Compiler()
# 		# compiled = compiler.expandUnderspecified(tempDataObj) # autofill data type/model information
# 		# output.append(compiled)
# 		output.append(tempDataObj.compiled)
# 	# return(output)
# 	recommendation["collection"] = lux.DataObjCollection(output)
# 	result.addResult(recommendation,dobj)
# 	return result

import lux
from lux.interestingness.valueBasedInterestingness import valueBasedInterestingness
# from compiler.Compiler import Compiler
'''
Shows possible visualizations when one attribute or filter from the current context is removed
'''
def generalize(dobj):
	# takes in a dataObject and generates a list of new dataObjects, each with a single measure from the original object removed
	# -->  return list of dataObjects with corresponding interestingness scores
	import scipy.stats
	import numpy as np
	result = lux.Result()
	recommendation = {"action":"Generalize",
						   "description":"Remove one attribute or filter to observe a more general trend."}
	output = []
	excludedColumns = []
	for i in range(0,len(dobj.spec)):
		if dobj.spec[i].className == "Column":
			columns = dobj.spec[i].columnName
			#have to split into two cases, if there is only a single variable in a Column, then its
			#columnName value will be a string instead of a list and needs to be handled differently
			if type(columns) == list:
				for column in columns:
					if column not in excludedColumns:
						tempDataObj = lux.DataObj(dobj.dataset, dobj.spec)
						tempDataObj.removeColumnFromSpecNew(column)
						excludedColumns.append(column)
						tempDataObj.score = 0.5#valueBasedInterestingness(tempDataObj)
						output.append(tempDataObj)
			elif type(columns) == str:
				if columns not in excludedColumns:
					tempDataObj = lux.DataObj(dobj.dataset, dobj.spec)
					tempDataObj.removeColumnFromSpecNew(columns)
					excludedColumns.append(columns)
					tempDataObj.score = 0.5#valueBasedInterestingness(tempDataObj)
		elif dobj.spec[i].className == "Row":
			newSpec = dobj.spec.copy()
			newSpec.pop(i)
			tempDataObj = lux.DataObj(dobj.dataset, newSpec)
			tempDataObj.score = 0.5#valueBasedInterestingness(tempDataObj)
		tempDataObj.compile() # need to recompile
		# compiler = Compiler()
		# compiled = compiler.expandUnderspecified(tempDataObj) # autofill data type/model information
		# output.append(compiled)
		output.append(tempDataObj.compiled)
	# return(output)
	recommendation["collection"] = lux.DataObjCollection(output)
	result.addResult(recommendation,dobj)
	return result