import lux
from lux.interestingness.interestingness import interestingness
from lux.view.View import View
from lux.view.ViewCollection import ViewCollection
from lux.executor.PandasExecutor import PandasExecutor
from lux.compiler.Compiler import Compiler
from lux.utils import utils
'''
Shows possible visualizations when filtered by categorical variables in the data object's dataset
'''
def filter(ldf):
	recommendation = {"action":"Filter",
						   "description":"Shows possible visualizations when filtered by categorical variables in the data object's dataset."}
	filters = utils.getFilterSpecs(ldf.context)
	filterValues = []
	output = []
	#if Row is specified, create visualizations where data is filtered by all values of the Row's categorical variable
	columnSpec = utils.getAttrsSpecs(ldf.viewCollection[0].specLst)
	if len(filters) > 0:
		completedFilters = []
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
						newFilter = lux.Spec(attribute = row.attribute, value = uniqueValues[i])
						newSpec.append(newFilter)
						tempView = View(newSpec)
						tempView.score = interestingness(tempView,ldf)
						output.append(tempView)
				completedFilters.append(row.attribute)
	#if Row is not specified, create filters using unique values from all categorical variables in the dataset
	else:
		categoricalVars = ldf.dataType['nominal']
		allCategoricalVars = ldf.dataType['nominal']

		for spec in columnSpec:
				if spec.attribute in allCategoricalVars:
					categoricalVars.remove(spec.attribute)
		for cat in categoricalVars:
			uniqueValues = ldf[cat].unique()
			for i in range(0, len(uniqueValues)):
				newSpec = columnSpec.copy()
				newFilter = lux.Spec(attribute=cat, value=uniqueValues[i])
				newSpec.append(newFilter)
				tempView = View(newSpec)
				tempView.score = interestingness(tempView,ldf)
				output.append(tempView)
	vc = lux.view.ViewCollection.ViewCollection(output)
	vc = Compiler.compile(ldf,vc,enumerateCollection=False)
	vc = vc.topK(10)
	PandasExecutor.execute(vc,ldf)
	recommendation["collection"] = vc
	# print(vc)
	return recommendation