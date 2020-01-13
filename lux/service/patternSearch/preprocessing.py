import lux
import pandas as pd
import math
def aggregate(dobj):
# find y axis then aggregate on it
	if dobj.getObjFromChannel("x") and dobj.getObjFromChannel("y"):

		xAxis = dobj.getObjFromChannel("x")[0].columnName
		yAxis = dobj.getObjFromChannel("y")[0].columnName

		dobj.transformedDataset = lux.Dataset(dobj.dataset.filename, dobj.dataset.schema)

		dobj.transformedDataset.df = dobj.dataset.df[[xAxis,yAxis]].groupby(xAxis,as_index=False).agg({yAxis:'mean'})

def interpolate(dobj, length):

	if dobj.getObjFromChannel("x") and dobj.getObjFromChannel("y"):

		xAxis = dobj.getObjFromChannel("x")[0].columnName
		yAxis = dobj.getObjFromChannel("y")[0].columnName

		df = dobj.transformedDataset.df

		if xAxis and yAxis:
			yVals = df[yAxis]
			xVals = df[xAxis]

			n = length

			interpolatedXVals = [0.0]*(length+1)
			interpolatedYVals = [0.0]*(length+1)

			granularity = (xVals[len(xVals)-1] - xVals[0]) / n

			count = 0

			for i in range(1,n):
				interpolatedX = xVals[0] + i * granularity
				interpolatedXVals[i] = interpolatedX

				while xVals[count] < interpolatedX:
					if(count < len(xVals)):
						count += 1
				if xVals[count] == interpolatedX:
					interpolatedYVals[i] = yVals[count]
				else:
					xDiff = xVals[count] - xVals[count-1]
					yDiff = yVals[count] - yVals[count-1]
					interpolatedYVals[i] = yVals[count-1] + (interpolatedX - xVals[count-1]) / xDiff * yDiff

			dobj.transformedDataset.df = pd.DataFrame(list(zip(interpolatedXVals, interpolatedYVals)),columns = [xAxis, yAxis])

# interpolate dataset

def normalize(dobj):

	if dobj.getObjFromChannel("y"):
		yAxis = dobj.getObjFromChannel("y")[0].columnName
		df = dobj.transformedDataset.df
		max = df[yAxis].max()
		min = df[yAxis].min()

		if(max == min or (max-min<1)):
			return

		dobj.transformedDataset.df[yAxis] = (df[yAxis] - min) / (max - min)
