import lux
import pandas as pd
import math
import numpy as np
from lux.view.ViewCollection import ViewCollection

def similarPattern(ldf,queryContext,topK=-1):
    '''
    Generates visualizations with similar patterns to a query visualization.

    Parameters
    ----------
    ldf : lux.luxDataFrame.LuxDataFrame
    	LuxDataFrame with underspecified context.

    queryContext: list[lux.Spec]
        context for specifying the visual query for the similarity search.

    topK: int
        number of visual recommendations to return.

    Returns
    -------
    recommendations : Dict[str,obj]
    	object with a collection of visualizations that result from the Similarity action
    '''
    rowSpecs = list(filter(lambda x: x.value != "", queryContext))
    if(len(rowSpecs) == 1):
        searchSpaceVC = ViewCollection(ldf.viewCollection.collection.copy())
        searchSpaceVC = searchSpaceVC.load(ldf)

        queryVC = ViewCollection(queryContext)
        queryVC = queryVC.load(ldf)        
        queryView = queryVC[0]
        preprocess(queryView)
        #for loop to create assign euclidean distance
        recommendation = {"action":"Similarity",
                               "description":"Show other charts that are visually similar to the Current View."}
        for view in searchSpaceVC:
            preprocess(view)
            view.score = euclideanDist(queryView, view)
        searchSpaceVC.normalizeScore(invertOrder=True)
        if(topK!=-1):
            searchSpaceVC = searchSpaceVC.topK(topK)
        recommendation["collection"] = searchSpaceVC
        return recommendation
    else:
        print("Query needs to have 1 row value")

def aggregate(view):
    '''
    Aggregates data values on the y axis so that the view is a time series

    Parameters
    ----------
    view : lux.view.View
        view that represents the candidate visualization
    Returns
    -------
    None
    '''
    if view.getAttrByChannel("x") and view.getAttrByChannel("y"):

        xAxis = view.getAttrByChannel("x")[0].attribute
        yAxis = view.getAttrByChannel("y")[0].attribute

        view.data = view.data[[xAxis,yAxis]].groupby(xAxis,as_index=False).agg({yAxis:'mean'}).copy()

def interpolate(view,length):
    '''
    Interpolates the view data so that the number of data points is fixed to a constant

    Parameters
    ----------
    view : lux.view.View
        view that represents the candidate visualization
    length : int
        number of points a view should have

    Returns
    -------
    None
    '''
    if view.getAttrByChannel("x") and view.getAttrByChannel("y"):

        xAxis = view.getAttrByChannel("x")[0].attribute
        yAxis = view.getAttrByChannel("y")[0].attribute

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
    '''
    Normalizes the view data so that the range of values is 0 to 1 for the view

    Parameters
    ----------
    view : lux.view.View
        view that represents the candidate visualization
    Returns
    -------
    None
    '''
    if view.getAttrByChannel("y"):
        yAxis = view.getAttrByChannel("y")[0].attribute
        max = view.data[yAxis].max()
        min = view.data[yAxis].min()
        if(max == min or (max-min<1)):
            return
        view.data[yAxis] = (view.data[yAxis] - min) / (max - min)

def euclideanDist(queryView,view):
    '''
    Calculates euclidean distance score for similarity between two views

    Parameters
    ----------
    queryView : lux.view.View
        view that represents the query pattern
    view : lux.view.View
        view that represents the candidate visualization

    Returns
    -------
    score : float
        eculidean distance score
    '''

    if queryView.getAttrByChannel("y") and view.getAttrByChannel("y"):

        viewYAxis = view.getAttrByChannel("y")[0].attribute
        queryYAxis = queryView.getAttrByChannel("y")[0].attribute

        viewVector = view.data[viewYAxis].values
        queryVector = queryView.data[queryYAxis].values
        score = np.linalg.norm(viewVector - queryVector)

        return score
    else:
        print("no y axis detected")
        return 0
def preprocess(view):
    '''
    Processes view data to allow similarity comparisons between visualizations

    Parameters
    ----------
    view : lux.view.View
        view that represents the candidate visualization
    Returns
    -------
    None
    '''
    aggregate(view)
    interpolate(view, 100)
    normalize(view)

