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

from lux.vis.VisList import VisList
from lux.vis.Vis import Vis
# from lux.core.frame import LuxDataFrame
from lux.implicit import implicit_plotter

import lux

from IPython.core.debugger import set_trace

def implicit_mre(ldf: lux.core.frame.LuxDataFrame):
    """
    Generates vis based off only most recent implicit action.

    Parameters
    ----------
    ldf : lux.core.frame
            LuxDataFrame with underspecified intent.

    Returns
    -------
    recommendations : Dict[str,obj]
            object with a collection of visualizations that result from the Implicit action.
    """
    # these events are cleansed when fetched 
    most_recent_event, col_list = ldf.history.get_implicit_intent(ldf.columns)
    str_desc = "Recommendedations based off code containing: <br/>"
    lux_vis = []
    used_cols = most_recent_event.cols if most_recent_event is not None else []

    # get unique vis for recent col ref 
    if most_recent_event:
        lux_vis = VisList([], ldf)
        vl, used_cols = implicit_plotter.generate_vis_from_signal(most_recent_event, ldf, col_list)
        
        lux_vis._collection.extend(vl._collection)
        str_desc += f"> Call to function '{most_recent_event.op_name}' in execution cell [{most_recent_event.ex_count}] <br/>"

    recommendation = {
        "action": "Implicit",
        "description": "",
        "long_description": "",
        "collection": lux_vis
    }
    
    return recommendation