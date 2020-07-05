import lux
from lux.interestingness.interestingness import interestingness
from lux.compiler.Compiler import Compiler
from lux.utils import utils

#for benchmarking
import time
def enhance(ldf):
	#for benchmarking
	if ldf.toggle_benchmarking == True:
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
	# Collect variables that already exist in the context
	attrSpecs = list(filter(lambda x: x.value=="" and x.attribute!="Record", ldf.context))
	if(len(attrSpecs)>2): # if there are too many column attributes, return don't generate Enhance recommendations
		recommendation["collection"] = []
		return recommendation
	query = ldf.context.copy()
	query = filters + attrSpecs
	query.append("?")
	vc = lux.view.ViewCollection.ViewCollection(query)
	vc = vc.load(ldf)
		
	# Then use the data populated in the view collection to compute score
	for view in vc: view.score = interestingness(view,ldf)
	
	vc = vc.topK(15)
	recommendation["collection"] = vc
	#for benchmarking
	if ldf.toggle_benchmarking == True:
		toc = time.perf_counter()
		print(f"Performed enhance action in {toc - tic:0.4f} seconds")
	return recommendation