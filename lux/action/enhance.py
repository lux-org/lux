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
	Given a set of views, generates possible visualizations when an additional attribute is added to the current vis.

	Parameters
	----------
	ldf : lux.luxDataFrame.LuxDataFrame
		LuxDataFrame with underspecified intent.

	Returns
	-------
	recommendations : Dict[str,obj]
		object with a collection of visualizations that result from the Enhance action.
	'''
	
	filters = utils.get_filter_specs(ldf.intent)
	# Collect variables that already exist in the intent
	attr_specs = list(filter(lambda x: x.value=="" and x.attribute!="Record", ldf.intent))
	fltr_str = [fltr.attribute+fltr.filter_op+fltr.value for fltr in filters]
	attr_str = [clause.attribute for clause in attr_specs]
	intended_attrs = '<p class="highlight-text">'+', '.join(attr_str+fltr_str)+'</p>'
	recommendation = {"action":"Enhance",
					"description":f"Add an attribute to {intended_attrs}."}
	if(len(attr_specs)>2): # if there are too many column attributes, return don't generate Enhance recommendations
		recommendation["collection"] = []
		return recommendation
	intent = ldf.intent.copy()
	intent = filters + attr_specs
	intent.append("?")
	vc = lux.vis.VisList.VisList(intent,ldf)
		
	# Then use the data populated in the vis list to compute score
	for view in vc: view.score = interestingness(view,ldf)
	
	vc = vc.topK(15)
	recommendation["collection"] = vc
	#for benchmarking
	if ldf.toggle_benchmarking == True:
		toc = time.perf_counter()
		print(f"Performed enhance action in {toc - tic:0.4f} seconds")
	return recommendation