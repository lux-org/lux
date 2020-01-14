import lux
from lux.dataObj.dataObj import DataObj
from lux.dataObj.dataObj import Row
from lux.dataObj.dataObj import Column

from lux.dataObj.DataObjCollection import DataObjCollection
from lux.interestingness.interestingness import interestingness
import pandas as pd
'''
Shows possible visualizations when an additional attribute is added to the current view
'''
def enhance(dobj):
	result = lux.Result()
	recommendation = {"action":"Enhance",
					"description":"Shows possible visualizations when an additional attribute is added to the current view."}
	quantitativeVars = dobj.dataset.dataType['quantitative']
	categoricalVars = dobj.dataset.dataType['categorical']
	output = []

	dobjVars = []
	for i in range(0, len(dobj.spec)):
		if dobj.spec[i].className == "Column":
			dobjVars.append(dobj.spec[i].columnName)
		elif dobj.spec[i].className == "Row":
			dobjVars.append(dobj.spec[i].fAttribute)

	#go through and add additional quantitative variable
	for qVar in quantitativeVars:
		if qVar not in dobjVars:
			newSpec = dobj.spec.copy()
			newSpec.append(Column(qVar))
			tempDataObj = DataObj(dobj.dataset, newSpec)
			tempDataObj.score = interestingness(tempDataObj)

			tempDataObj.compile()
			output.append(tempDataObj.compiled)

	#go through and add additional categorical variable
	for cVar in categoricalVars:
		if cVar not in dobjVars:
			newSpec = dobj.spec.copy()
			newSpec.append(Column(cVar))
			tempDataObj = DataObj(dobj.dataset, newSpec)
			if (dobj.dataset.cardinality[cVar]<10):
				tempDataObj.score = interestingness(tempDataObj)
			else:
				tempDataObj.score = -1 

			tempDataObj.compile()
			output.append(tempDataObj.compiled)
	output = DataObjCollection(output)
	output.sort(removeInvalid=True)
	recommendation["collection"] = output
	result.addResult(recommendation,dobj)
	return result