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
import scipy.stats
import numpy as np
from lux.view.View import View
from lux.compiler.Compiler import Compiler
from lux.executor.PandasExecutor import PandasExecutor

# from compiler.Compiler import Compiler
'''
Shows possible visualizations when one attribute or filter from the current context is removed
'''
def generalize(ldf):
	# takes in a dataObject and generates a list of new dataObjects, each with a single measure from the original object removed
	# -->  return list of dataObjects with corresponding interestingness scores

	recommendation = {"action":"Generalize",
						   "description":"Remove one attribute or filter to observe a more general trend."}
	output = []
	excludedColumns = []
	columnSpec = ldf.getAttrsSpecs()
	rowSpecs = ldf.getFilterSpecs()
	# if we do no have enough column attributes or too many, return no views.
	if(len(columnSpec)<2 or len(columnSpec)>4):
		recommendation["collection"] = []
		return recommendation
	for spec in columnSpec:
		columns = spec.attribute
		if type(columns) == list:
			for column in columns:
				if column not in excludedColumns:
					tempView = View(ldf.context)
					tempView.removeColumnFromSpecNew(column)
					excludedColumns.append(column)
					tempView.score = 0.5  # valueBasedInterestingness(tempDataObj)
					output.append(tempView)
		elif type(columns) == str:
			if columns not in excludedColumns:
				tempView = View(ldf.context)
				tempView.removeColumnFromSpecNew(columns)
				excludedColumns.append(columns)
				tempView.score = 0.5  # valueBasedInterestingness(tempDataObj)
		output.append(tempView)
	for i, spec in enumerate(rowSpecs):
		newSpec = ldf.context.copy()
		newSpec.pop(i)
		tempView = View(newSpec)
		tempView.score = 0.5  # valueBasedInterestingness(tempDataObj)
		output.append(tempView)
	vc = lux.view.ViewCollection.ViewCollection(output)
	vc = Compiler.compile(ldf,vc,enumerateCollection=False)
	PandasExecutor.execute(vc,ldf)
	recommendation["collection"] = vc
	return recommendation