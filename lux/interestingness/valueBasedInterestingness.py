def valueBasedInterestingness(dobj):
	import pandas as pd
	#checks to see if a filter is applied to the data object, if no filter just use
	#basic aggregate function
	if len(dobj.getObjByRowColType("Row")) == 0:
		aggVal = list(dobj.dataset.df[dobj.spec[0].columnName].sum(skipna = True))[0]
		return(aggVal)
	else:
		row = dobj.getObjByRowColType("Row")[0]
		originalData = dobj.dataset.df
		filteredData = dobj.dataset.df[dobj.dataset.df[row.fAttribute] == row.fVal]
		if len(filteredData) != 0:
			filteredAggVal = filteredData[dobj.spec[0].columnName].sum(skipna = True)
			return(filteredAggVal)
		else:
			return(0)

