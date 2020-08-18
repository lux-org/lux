import lux
from lux.interestingness.interestingness import interestingness
from lux.processor.Compiler import Compiler
from lux.utils import utils

#for benchmarking
import time
def enhance(ldf):
	'''
	Given a set of views, generates possible visualizations when an additional attribute is added to the current vis.

	Parameters
	----------
	ldf : lux.core.frame
		LuxDataFrame with underspecified intent.

	Returns
	-------
	recommendations : Dict[str,obj]
		object with a collection of visualizations that result from the Enhance action.
	'''
	
	filters = utils.get_filter_specs(ldf._intent)
	# Collect variables that already exist in the intent
	attr_specs = list(filter(lambda x: x.value=="" and x.attribute!="Record", ldf._intent))
	fltr_str = [fltr.attribute+fltr.filter_op+str(fltr.value) for fltr in filters]
	attr_str = [clause.attribute for clause in attr_specs]
	intended_attrs = '<p class="highlight-intent">'+', '.join(attr_str+fltr_str)+'</p>'
	if (len(attr_specs)==1):
		recommendation = {"action":"Enhance",
						"description":f"Augmenting current {intended_attrs} intent with additional attribute."}
	elif(len(attr_specs)==2):
		recommendation = {"action":"Enhance",
						"description":f"Further breaking down current {intended_attrs} intent by additional attribute."}
	elif(len(attr_specs)>2): # if there are too many column attributes, return don't generate Enhance recommendations
		recommendation = {"action":"Enhance"}
		recommendation["collection"] = []
		return recommendation
	intent = ldf._intent.copy()
	intent = filters + attr_specs
	intent.append("?")
	vc = lux.vis.VisList.VisList(intent,ldf)
		
	# Then use the data populated in the vis list to compute score
	for view in vc: view.score = interestingness(view,ldf)
	
	vc = vc.topK(15)
	recommendation["collection"] = vc
	return recommendation