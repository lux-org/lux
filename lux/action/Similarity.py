import lux
import pandas as pd
import math
import numpy as np
from lux.view.ViewCollection import ViewCollection

def similar_pattern(ldf, queryContext, topK=-1):
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
    row_specs = list(filter(lambda x: x.value != "", queryContext))
    if(len(row_specs) == 1):
        search_space_vc = ViewCollection(ldf.current_view.collection.copy())
        search_space_vc = search_space_vc.load(ldf)

        query_vc = ViewCollection(queryContext)
        query_vc = query_vc.load(ldf)       
        query_view = query_vc[0]
        preprocess(queryView)
        #for loop to create assign euclidean distance
        recommendation = {"action":"Similarity",
                               "description":"Show other charts that are visually similar to the Current View."}
        for view in search_space_vc:
            preprocess(view)
            view.score = euclidean_dist(query_view, view)
        search_space_vc.normalize_score(invert_order=True)
        if(topK!=-1):
            search_space_vc = search_space_vc.topK(topK)
        recommendation["collection"] = search_space_vc
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
    if view.get_attr_by_channel("x") and view.get_attr_by_channel("y"):

        xAxis = view.get_attr_by_channel("x")[0].attribute
        yAxis = view.get_attr_by_channel("y")[0].attribute

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
    if view.get_attr_by_channel("x") and view.get_attr_by_channel("y"):

        xAxis = view.get_attr_by_channel("x")[0].attribute
        yAxis = view.get_attr_by_channel("y")[0].attribute

        if xAxis and yAxis:
            yVals = view.data[yAxis]
            xVals = view.data[xAxis]
            n = length

            interpolated_x_vals = [0.0]*(length)
            interpolated_y_vals = [0.0]*(length)

            granularity = (xVals[len(xVals)-1] - xVals[0]) / n

            count = 0

            for i in range(0,n):
                interpolated_x = xVals[0] + i * granularity
                interpolated_x_vals[i] = interpolated_x

                while xVals[count] < interpolated_x:
                    if(count < len(xVals)):
                        count += 1
                if xVals[count] == interpolated_x:
                    interpolated_y_vals[i] = yVals[count]
                else:
                    x_diff = xVals[count] - xVals[count-1]
                    yDiff = yVals[count] - yVals[count-1]
                    interpolated_y_vals[i] = yVals[count-1] + (interpolated_x - xVals[count-1]) / x_diff * yDiff
            view.data = pd.DataFrame(list(zip(interpolated_x_vals, interpolated_y_vals)),columns = [xAxis, yAxis])

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
    if view.get_attr_by_channel("y"):
        y_axis = view.get_attr_by_channel("y")[0].attribute
        max = view.data[y_axis].max()
        min = view.data[y_axis].min()
        if(max == min or (max-min<1)):
            return
        view.data[y_axis] = (view.data[y_axis] - min) / (max - min)

def euclidean_dist(query_view, view):
    '''
    Calculates euclidean distance score for similarity between two views

    Parameters
    ----------
    query_view : lux.view.View
        view that represents the query pattern
    view : lux.view.View
        view that represents the candidate visualization

    Returns
    -------
    score : float
        euclidean distance score
    '''

    if query_view.get_attr_by_channel("y") and view.get_attr_by_channel("y"):

        view_y_axis = view.get_attr_by_channel("y")[0].attribute
        query_y_axis = query_view.get_attr_by_channel("y")[0].attribute

        view_vector = view.data[view_y_axis].values
        query_vector = query_view.data[query_y_axis].values
        score = np.linalg.norm(view_vector - query_vector)

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

