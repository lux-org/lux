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
	# vizCollection = dobj.compiled.collection
	# #list that will contain the DataObjs to be returned in the output
	# outputDataCollection = []
	# #list to keep track of columns and rows already included in the output (ensure no repeat graphs)
	# columnNames = []
	# rowNames = []
	# for obj in vizCollection:
	# 	#have to remove count() column from the specification first
	# 	obj.removeColumnFromSpec("count()")

	# 	columns = obj.getObjByRowColType("Column")
	# 	rows = obj.getObjByRowColType("Row")
	# 	numCol = len(columns)
	# 	numRow = len(rows)
	# 	numRowCol = numCol + numRow
	# 	#iterates through the columns of the data object and removes one column at a time if the number of
	# 	#rows and columns in the data object is greater than 1
	# 	if numRowCol > 1:
	# 		#if there is more than one column in a data object, iterate through the columns and remove them one by one
	# 		if numCol > 1:
	# 			for column in columns:
	# 				tempDataObj = lux.DataObj(obj.dataset, obj.spec)
	# 				tempDataObj.removeColumnFromSpec(column.columnName)

	# 				if len(tempDataObj.spec) > 0 and tempDataObj.spec[0].columnName not in columnNames:
	# 					tempDataObj.score = valueBasedInterestingness(tempDataObj)
	# 					outputDataCollection.append(tempDataObj)
	# 					columnNames.append(tempDataObj.spec[0].columnName)
	# 		else:
	# 			columnNames.append(obj.spec[0].columnName)

	# 		#iterates through the rows of the data object and removes one row at a time
	# 		for row in rows:
	# 			#use the original dataset before any filtering occurs
	# 			tempDataObj = lux.DataObj(dobj.dataset, obj.getObjByRowColType("Column"))
	# 			#remove current row from the data object's specification
	# 			originalRows = obj.getObjByRowColType("Row")
	# 			newRows = originalRows.remove(row)

	# 			#only adds rows to the temp data object specifications if there are rows to add
	# 			if newRows != None:
	# 				tempDataObj.spec.append(newRows)

	# 			if len(tempDataObj.spec) > 0 and (newRows not in rowNames or newRows == None):
	# 				tempDataObj.score = valueBasedInterestingness(tempDataObj)
	# 				outputDataCollection.append(tempDataObj)
	# 				rowNames.append(newRows)

	# 	#if the data object only contains a single column, calculate its interestingness and add to the output
	# 	else:
	# 		obj.score = valueBasedInterestingness(obj)
	# 		outputDataCollection.append(obj)

	# return(outputDataCollection)