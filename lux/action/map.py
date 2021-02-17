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

from lux.interestingness.interestingness import interestingness
from lux.vis.VisList import VisList
import lux
from lux.utils import utils


def geomap(ldf, ignore_transpose: bool = True):
    """
    Generates map distributions of different attributes in the dataframe.

    Parameters
    ----------
    ldf : lux.core.frame
            LuxDataFrame with underspecified intent.

    data_type_constraint: str
            Controls the type of distribution chart that will be rendered.

    Returns
    -------
    recommendations : Dict[str,obj]
            object with a collection of visualizations that result from the Distribution action.
    """
    import numpy as np

    ignore_rec_flag = False
    possible_attributes = [
        c
        for c in ldf.columns
        if ldf.data_type[c] == "geographical" and ldf.cardinality[c] > 5 and c != "Number of Records"
    ]
    recommendation = {
        "action": "Geographic",
        "description": "Show proportional symbol maps of <p class='highlight-descriptor'>geographic</p>  attributes.",
    }

    if len(ldf) < 5 or len(possible_attributes) < 2:
        ignore_rec_flag = True
    if ignore_rec_flag or not valid_geographical(possible_attributes):
        recommendation["collection"] = []
        return recommendation

    intent = [
        lux.Clause(attribute="latitude", data_model="measure", channel="x"),
        lux.Clause(attribute="longitude", data_model="measure", channel="y"),
        lux.Clause("?"),
        lux.Clause("?", data_model="measure"),
    ]

    vlist = VisList(intent, ldf)
    for i in range(len(vlist)):
        vis = vlist[i]
        if has_secondary_geographical_attribute(vis):
            vis._mark = "geographical"
            measures = vis.get_attr_by_data_model("measure")
            msr1, msr2 = measures[0].attribute, measures[1].attribute
            vis.score = interestingness(vis, ldf)
        else:
            vis.score = -1

    vlist.sort()
    recommendation["collection"] = vlist
    return recommendation


def has_secondary_geographical_attribute(vis):
    assert len(vis.intent) >= 3
    secondary_attributes = {"state", "country"}
    color = vis.intent[2].get_attr()
    if color in secondary_attributes:
        return True
    return False


def valid_geographical(possible_attributes):
    lat, long = {"latitude"}, {"longitude"}
    possible_attributes = set(possible_attributes)
    has_lat, has_long = (
        len(lat.intersection(possible_attributes)) > 0,
        len(long.intersection(possible_attributes)) > 0,
    )
    var = True if has_lat and has_long and len(possible_attributes) == 2 else False
    return var
