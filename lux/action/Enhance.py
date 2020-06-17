import lux
from lux.interestingness.interestingness import interestingness
from lux.compiler.Compiler import Compiler
from lux.utils import utils

#for benchmarking
import time
def enhance(ldf):
	#for benchmarking
	if ldf.toggleBenchmarking == True:
		tic = time.perf_counter()
	'''
	Given a set of views, generates possible visualizations when an additional attribute is added to the current view.

	Parameters
	----------
	ldf : lux.luxDataFrame.LuxDataFrame
		LuxDataFrame with underspecified context.

	Returns
	-------
	recommendations : Dict[str,obj]
		object with a collection of visualizations that result from the Enhance action.
	'''
	recommendation = {"action":"Enhance",
					"description":"Shows possible visualizations when an additional attribute is added to the current view."}
	filters = utils.getFilterSpecs(ldf.context)
	output = []
	# Collect variables that already exist in the context
	context = utils.getAttrsSpecs(ldf.context)
	# context = [spec for spec in context if isinstance(spec.attribute,str)]
	existingVars = [spec.attribute for spec in context]
	# if we too many column attributes, return no views.
	if(len(context)>2):
		recommendation["collection"] = []
		return recommendation

	# First loop through all variables to create new view collection
	for qVar in list(ldf.columns):
		if qVar not in existingVars and ldf.dataTypeLookup[qVar] != "temporal":
			cxtNew = context.copy()
			cxtNew.append(lux.Spec(attribute = qVar))
			cxtNew.extend(filters)
			view = lux.view.View.View(cxtNew)
			output.append(view)
	vc = lux.view.ViewCollection.ViewCollection(output)
	vc = vc.load(ldf)
		
	# Then use the data populated in the view collection to compute score
	for view in vc:
		view.score = interestingness(view,ldf)
		# TODO: if (ldf.dataset.cardinality[cVar]>10): score is -1. add in interestingness
	
	vc = vc.topK(15)
	recommendation["collection"] = vc
	#for benchmarking
	if ldf.toggleBenchmarking == True:
		toc = time.perf_counter()
		print(f"Performed enhance action in {toc - tic:0.4f} seconds")
	return recommendation