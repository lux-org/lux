def valueBasedInterestingness(view,ldf):
	#checks to see if a filter is applied to the data object, if no filter just use
	#basic aggregate function
	if len(view.getAttrsSpecs()) == 0:
		aggVal = list(ldf[view.spec[0].attribute].sum(skipna = True))[0]
		return(aggVal)
	else:
		row = view.getFilterSpecs()[0]
		originalData = ldf
		filteredData = ldf[ldf[row.attribute] == row.value]
		if len(filteredData) != 0:
			filteredAggVal = filteredData[view.specLst[0].attribute].sum(skipna = True)
			return(filteredAggVal)
		else:
			return(0)

