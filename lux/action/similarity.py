#  Copyright 2019-2020 The Lux Authors.
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import lux
import pandas as pd
import math
import numpy as np
from lux.vis.VisList import VisList

def similar_pattern(ldf, intent, topK=-1):
    '''
    Generates visualizations with similar patterns to a query visualization.

    Parameters
    ----------
    ldf : lux.core.frame
    	LuxDataFrame with underspecified intent.

    intent: list[lux.Clause]
        intent for specifying the visual query for the similarity search.

    topK: int
        number of visual recommendations to return.

    Returns
    -------
    recommendations : Dict[str,obj]
    	object with a collection of visualizations that result from the Similarity action
    '''
    row_specs = list(filter(lambda x: x.value != "", intent))
    if(len(row_specs) == 1):
        search_space_vc = VisList(ldf.current_vis.collection.copy(),ldf)

        query_vc = VisList(intent,ldf)     
        query_vis = query_vc[0]
        preprocess(query_vis)
        #for loop to create assign euclidean distance
        recommendation = {"action":"Similarity",
                               "description":"Show other charts that are visually similar to the Current vis."}
        for vis in search_space_vc:
            preprocess(vis)
            vis.score = euclidean_dist(query_vis, vis)
        search_space_vc.normalize_score(invert_order=True)
        if(topK!=-1):
            search_space_vc = search_space_vc.topK(topK)
        recommendation["collection"] = search_space_vc
        return recommendation
    else:
        print("Query needs to have 1 row value")

def aggregate(vis):
    '''
    Aggregates data values on the y axis so that the vis is a time series

    Parameters
    ----------
    vis : lux.vis.Vis
        vis that represents the candidate visualization
    Returns
    -------
    None
    '''
    if vis.get_attr_by_channel("x") and vis.get_attr_by_channel("y"):

        xAxis = vis.get_attr_by_channel("x")[0].attribute
        yAxis = vis.get_attr_by_channel("y")[0].attribute

        vis.data = vis.data[[xAxis,yAxis]].groupby(xAxis,as_index=False).agg({yAxis:'mean'}).copy()

def interpolate(vis,length):
    '''
    Interpolates the vis data so that the number of data points is fixed to a constant

    Parameters
    ----------
    vis : lux.vis.Vis
        vis that represents the candidate visualization
    length : int
        number of points a vis should have

    Returns
    -------
    None
    '''
    if vis.get_attr_by_channel("x") and vis.get_attr_by_channel("y"):

        xAxis = vis.get_attr_by_channel("x")[0].attribute
        yAxis = vis.get_attr_by_channel("y")[0].attribute

        if xAxis and yAxis:
            yVals = vis.data[yAxis]
            xVals = vis.data[xAxis]
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
            vis.data = pd.DataFrame(list(zip(interpolated_x_vals, interpolated_y_vals)),columns = [xAxis, yAxis])

# interpolate dataset

def normalize(vis):
    '''
    Normalizes the vis data so that the range of values is 0 to 1 for the vis

    Parameters
    ----------
    vis : lux.vis.Vis
        vis that represents the candidate visualization
    Returns
    -------
    None
    '''
    if vis.get_attr_by_channel("y"):
        y_axis = vis.get_attr_by_channel("y")[0].attribute
        max = vis.data[y_axis].max()
        min = vis.data[y_axis].min()
        if(max == min or (max-min<1)):
            return
        vis.data[y_axis] = (vis.data[y_axis] - min) / (max - min)

def euclidean_dist(query_vis, vis):
    '''
    Calculates euclidean distance score for similarity between two visualizations

    Parameters
    ----------
    query_vis : lux.vis.Vis
        vis that represents the query pattern
    vis : lux.vis.Vis
        vis that represents the candidate visualization

    Returns
    -------
    score : float
        euclidean distance score
    '''

    if query_vis.get_attr_by_channel("y") and vis.get_attr_by_channel("y"):

        vis_y_axis = vis.get_attr_by_channel("y")[0].attribute
        query_y_axis = query_vis.get_attr_by_channel("y")[0].attribute

        vis_vector = vis.data[vis_y_axis].values
        query_vector = query_vis.data[query_y_axis].values
        score = np.linalg.norm(vis_vector - query_vector)

        return score
    else:
        print("no y axis detected")
        return 0
def preprocess(vis):
    '''
    Processes vis data to allow similarity comparisons between visualizations

    Parameters
    ----------
    vis : lux.vis.Vis
        vis that represents the candidate visualization
    Returns
    -------
    None
    '''
    aggregate(vis)
    interpolate(vis, 100)
    normalize(vis)

