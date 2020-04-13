# import lux
# from lux.interestingness.interestingness import interestingness
# import pandas as pd
# '''
# Shows possible visualizations when filtered by categorical variables in the data object's dataset
# '''
# def filter(dobj):
# 	result = lux.Result()
# 	recommendation = {"action":"Filter",
# 						   "description":"Shows possible visualizations when filtered by categorical variables in the data object's dataset."}
# 	filters = dobj.getObjByRowColType("Row")
# 	filterValues = []
# 	output = []
# 	#if Row is specified, create visualizations where data is filtered by all values of the Row's categorical variable
# 	if len(filters) > 0:
# 		completedFilters = []
# 		columnSpec = dobj.getObjByRowColType("Column")
# 		#get unique values for all categorical values specified and creates corresponding filters
# 		for row in filters:
# 			if row.fAttribute not in completedFilters:
# 				uniqueValues = dobj.dataset.df[row.fAttribute].unique()
# 				filterValues.append(row.fVal)
# 				#creates new data objects with new filters
# 				for i in range(0, len(uniqueValues)):
# 					if uniqueValues[i] not in filterValues:
# 						#create new Data Object
# 						newSpec = columnSpec.copy()
# 						newFilter = lux.Row(fAttribute = row.fAttribute, fVal = uniqueValues[i])
# 						newSpec.append(newFilter)
# 						tempDataObj = lux.DataObj(dobj.dataset, newSpec)
# 						tempDataObj.score = interestingness(tempDataObj)
#
# 						#recompile the new Data Object before appending to output
# 						tempDataObj.compile()
# 						output.append(tempDataObj.compiled)
# 				completedFilters.append(row.fAttribute)
# 	#if Row is not specified, create filters using unique values from all categorical variables in the dataset
# 	else:
# 		categoricalVars = dobj.dataset.dataType['nominal']
# 		columnSpec = dobj.getObjByRowColType("Column")
# 		for cat in categoricalVars:
# 			uniqueValues = dobj.dataset.df[cat].unique()
# 			for i in range(0, len(uniqueValues)):
# 				newSpec = columnSpec.copy()
# 				newFilter = lux.Row(fAttribute = cat, fVal = uniqueValues[i])
# 				newSpec.append(newFilter)
# 				tempDataObj = lux.DataObj(dobj.dataset, newSpec)
# 				tempDataObj.score = interestingness(tempDataObj)
#
# 				tempDataObj.compile()
# 				output.append(tempDataObj.compiled)
# 	outputDataObjCol = lux.DataObjCollection(output)
# 	outputDataObjCol = outputDataObjCol.topK(5)
# 	recommendation["collection"] = outputDataObjCol
# 	result.addResult(recommendation,dobj)
# 	return result

import lux
from lux.interestingness.interestingness import interestingness
from lux.view.View import View
from lux.view.ViewCollection import ViewCollection
from lux.executor.PandasExecutor import PandasExecutor
from lux.compiler.Compiler import Compiler
'''
Shows possible visualizations when filtered by categorical variables in the data object's dataset
'''
def filter(ldf):
	recommendation = {"action":"Filter",
						   "description":"Shows possible visualizations when filtered by categorical variables in the data object's dataset."}
	filters = ldf.getFilterSpecs()
	filterValues = []
	output = []
	#if Row is specified, create visualizations where data is filtered by all values of the Row's categorical variable
	if len(filters) > 0:
		completedFilters = []
		columnSpec = ldf.getAttrsSpecs()
		#get unique values for all categorical values specified and creates corresponding filters
		for row in filters:
			if row.attribute not in completedFilters:
				uniqueValues = ldf[row.attribute].unique()
				filterValues.append(row.value)
				#creates new data objects with new filters
				for i in range(0, len(uniqueValues)):
					if uniqueValues[i] not in filterValues:
						#create new Data Object
						newSpec = columnSpec.copy()
						newFilter = lux.Spec(attribute = row.attribute, value = uniqueValues[i], type = "value")
						newSpec.append(newFilter)
						tempView = View(newSpec)
						tempView.score = interestingness(tempView,ldf)
						output.append(tempView)
				completedFilters.append(row.attribute)
	#if Row is not specified, create filters using unique values from all categorical variables in the dataset
	else:
		categoricalVars = ldf.dataType['nominal']
		columnSpec = ldf.getAttrsSpecs()
		for cat in categoricalVars:
			uniqueValues = ldf[cat].unique()
			for i in range(0, len(uniqueValues)):
				newSpec = columnSpec.copy()
				newFilter = lux.Spec(attribute=cat, value=uniqueValues[i], type = "value")
				newSpec.append(newFilter)
				tempView = View(newSpec)
				tempView.score = interestingness(tempView,ldf)
				output.append(tempView)
	vc = lux.view.ViewCollection.ViewCollection(output)
	vc = Compiler.compile(ldf,vc,enumerateCollection=False)
	vc = vc.topK(20)
	PandasExecutor.execute(vc,ldf)
	recommendation["collection"] = vc
	# print(vc)
	return recommendation