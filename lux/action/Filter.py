import lux
from lux.interestingness.interestingness import interestingness
from lux.view.View import View
from lux.view.ViewCollection import ViewCollection
from lux.compiler.Compiler import Compiler
from lux.utils import utils

#for benchmarking
import time

def filter(ldf):
	#for benchmarking
	if ldf.toggleBenchmarking == True:
		tic = time.perf_counter()
	'''
	Iterates over all possible values of a categorical variable and generates visualizations where each categorical value filters the data.

	Parameters
	----------
	ldf : lux.luxDataFrame.LuxDataFrame
		LuxDataFrame with underspecified context.

	Returns
	-------
	recommendations : Dict[str,obj]
		object with a collection of visualizations that result from the Filter action.
	'''
	recommendation = {"action":"Filter",
						   "description":"Shows possible visualizations when filtered by categorical variables in the data object's dataset."}
	filters = utils.getFilterSpecs(ldf.context)
	filterValues = []
	output = []
	#if Row is specified, create visualizations where data is filtered by all values of the Row's categorical variable
	columnSpec = utils.getAttrsSpecs(ldf.viewCollection[0].specLst)
	columnSpecAttr = map(lambda x: x.attribute,columnSpec)
	if len(filters) > 0:
		completedFilters = []
		#get unique values for all categorical values specified and creates corresponding filters
		for row in filters:
			if row.attribute not in completedFilters:
				uniqueValues = ldf.uniqueValues[row.attribute]
				filterValues.append(row.value)
				#creates new data objects with new filters
				for i in range(0, len(uniqueValues)):
					if uniqueValues[i] not in filterValues:
						#create new Data Object
						newSpec = columnSpec.copy()
						newFilter = lux.Spec(attribute = row.attribute, value = uniqueValues[i])
						newSpec.append(newFilter)
						tempView = View(newSpec)
				completedFilters.append(row.attribute)
				output.append(tempView)
	#if Row is not specified, create filters using unique values from all categorical variables in the dataset
	else:
		categoricalVars = []
		for col in list(ldf.columns):
			# if cardinality is not too high, and attribute is not one of the X,Y (specified) column
			if ldf.cardinality[col]<40 and col not in columnSpecAttr:
				categoricalVars.append(col)
		for cat in categoricalVars:
			uniqueValues = ldf.uniqueValues[cat]
			for i in range(0, len(uniqueValues)):
				newSpec = columnSpec.copy()
				newFilter = lux.Spec(attribute=cat, filterOp="=",value=uniqueValues[i])
				newSpec.append(newFilter)
				tempView = View(newSpec)
				output.append(tempView)
	vc = lux.view.ViewCollection.ViewCollection(output)
	vc = vc.load(ldf)
	for view in vc:
		view.score = interestingness(view,ldf)
	vc = vc.topK(15)
	recommendation["collection"] = vc
	
	#for benchmarking
	if ldf.toggleBenchmarking == True:
		toc = time.perf_counter()
		print(f"Performed filter action in {toc - tic:0.4f} seconds")
	return recommendation