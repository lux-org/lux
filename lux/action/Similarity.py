import lux
import pandas as pd
import math
import numpy as np
from lux.executor.PandasExecutor import PandasExecutor
from lux.view.ViewCollection import ViewCollection
def aggregate(view):
# find y axis then aggregate on it
    if view.getObjFromChannel("x") and view.getObjFromChannel("y"):

        xAxis = view.getObjFromChannel("x")[0].attribute
        yAxis = view.getObjFromChannel("y")[0].attribute

        view.data = view.data[[xAxis,yAxis]].groupby(xAxis,as_index=False).agg({yAxis:'mean'}).copy()

def interpolate(view,length):

    if view.getObjFromChannel("x") and view.getObjFromChannel("y"):

        xAxis = view.getObjFromChannel("x")[0].attribute
        yAxis = view.getObjFromChannel("y")[0].attribute

        if xAxis and yAxis:
            yVals = view.data[yAxis]
            xVals = view.data[xAxis]
            n = length

            interpolatedXVals = [0.0]*(length)
            interpolatedYVals = [0.0]*(length)

            granularity = (xVals[len(xVals)-1] - xVals[0]) / n

            count = 0

            for i in range(0,n):
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
            view.data = pd.DataFrame(list(zip(interpolatedXVals, interpolatedYVals)),columns = [xAxis, yAxis])

# interpolate dataset

def normalize(view):

    if view.getObjFromChannel("y"):
        yAxis = view.getObjFromChannel("y")[0].attribute
        max = view.data[yAxis].max()
        min = view.data[yAxis].min()
        if(max == min or (max-min<1)):
            return
        view.data[yAxis] = (view.data[yAxis] - min) / (max - min)

def euclideanDist(queryView,view):

    if queryView.getObjFromChannel("y") and view.getObjFromChannel("y"):

        viewYAxis = view.getObjFromChannel("y")[0].attribute
        queryYAxis = queryView.getObjFromChannel("y")[0].attribute

        viewVector = view.data[viewYAxis].values
        queryVector = queryView.data[queryYAxis].values
        score = np.linalg.norm(viewVector - queryVector)

        return score
    else:
        print("no y axis detected")
        return 0
def preprocess(view):
    aggregate(view)
    interpolate(view, 100)
    normalize(view)
def similarPattern(ldf,queryContext,topK=-1):
    rowSpecs = list(filter(lambda x: x.value != "", queryContext))
    if(len(rowSpecs) == 1):
        searchSpaceVC = ViewCollection(ldf.viewCollection.collection.copy())
        PandasExecutor.execute(searchSpaceVC,ldf)

        ldf.setContext(queryContext)
        queryVC = ldf.viewCollection
        PandasExecutor.execute(queryVC, ldf)
        queryView = queryVC[0]
        preprocess(queryView)
        #for loop to create assign euclidean distance
        recommendation = {"action":"Similarity",
                               "description":"Show other charts that are visually similar to the Current View."}
        for view in searchSpaceVC:
            preprocess(view)
            view.score = euclideanDist(queryView, view)
        searchSpaceVC.normalizeScore(invertOrder=True)
        searchSpaceVC.sort(removeInvalid=True)
        if(topK!=-1):
            searchSpaceVC = searchSpaceVC.topK(topK)
        recommendation["collection"] = searchSpaceVC
        return recommendation
    else:
        print("Query needs to have 1 row value")
