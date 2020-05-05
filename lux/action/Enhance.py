import lux
from lux.interestingness.interestingness import interestingness
from lux.compiler.Compiler import Compiler
from lux.executor.PandasExecutor import PandasExecutor
from lux.executor.SQLExecutor import SQLExecutor
from lux.utils import utils
'''
Shows possible visualizations when an additional attribute is added to the current view
'''
def enhance(ldf):
	recommendation = {"action":"Enhance",
					"description":"Shows possible visualizations when an additional attribute is added to the current view."}
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
	for qVar in ldf.columns:
		if qVar not in existingVars and ldf.dataTypeLookup[qVar] != "temporal":
			cxtNew = context.copy()
			cxtNew.append(lux.Spec(attribute = qVar))
			view = lux.view.View.View(cxtNew)
			output.append(view)
	vc = lux.view.ViewCollection.ViewCollection(output)
	vc = Compiler.compile(ldf,vc,enumerateCollection=False)
	
	if ldf.executorType == "SQL":
		SQLExecutor.execute(vc,ldf)
	elif ldf.executorType == "Pandas":
		PandasExecutor.execute(vc,ldf)
		
	# Then use the data populated in the view collection to compute score
	for view in vc:
		view.score = interestingness(view,ldf)
		output.append(view)
		# TODO: if (ldf.dataset.cardinality[cVar]>10): score is -1. add in interestingness
	
	vc = vc.topK(10)
	vc.sort(removeInvalid=True)
	recommendation["collection"] = vc
	return recommendation