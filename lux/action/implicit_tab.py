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
import lux
import itertools
import numpy as np

from IPython.core.debugger import set_trace

def implicit_tab(ldf):
    """
    Generates bar chart distributions of different attributes in the dataframe.

    Parameters
    ----------
    ldf : lux.core.frame
            LuxDataFrame with underspecified intent.

    Returns
    -------
    recommendations : Dict[str,obj]
            object with a collection of visualizations that result from the Distribution action.
    """

    # TODO get this df name from somwehere or start using ids maybe?
    most_recent_signal, col_list = lux.config.code_tracker.get_implicit_intent(id(ldf))
    str_desc = "Recommendedations based off this code: <br/>"
    lux_vis = []

    if most_recent_signal:
        lux_vis = VisList([], ldf)

        # get vis for most recent 
        vl = generate_vis_from_signal(most_recent_signal, ldf)
        if vl:
            lux_vis._collection.extend(vl._collection)
            str_desc += f"> {most_recent_signal.code_str} <br/>"
        
        # get vis for columns
        if col_list:
            col_vis_l = []
            #max_score = len(col_vis_l)
            for i, c in enumerate(col_list):
                col_v = Vis( [lux.Clause(c)] )
                #col_v.score = max_score - i
                col_vis_l.append(col_v)
                str_desc += f"> ...lines with {c}... <br/>"
            
            vl_2 = VisList(col_vis_l, ldf)
            lux_vis._collection.extend(vl_2._collection)
        
        lux_vis.remove_duplicates()
        lux_vis.sort()


    # for vis in i_vis_list:
    #     vis.score = interestingness(vis, ldf)
    # vlist.sort()

    recommendation = {
        "action": "Implicit",
        "description": "Show visualizations based off your recent <p class='highlight-descriptor'>code history</p>.",
        "long_description": str_desc,
        "collection": lux_vis
    }
    
    return recommendation

def generate_vis_from_signal(signal, ldf):
    """
     "df_name cols f_name f_arg_dict ex_order"
    """
    # set_trace()
    vis_list = []
    if signal.f_name == "value_counts" or signal.f_name == "unique":
        
        clauses = []
        # for vc should only be one col, but if multiple use generic recs
        if len(signal.cols) > 1:
            clauses = [lux.Clause(attribute=i) for i in signal.cols]
        elif len(signal.cols) == 1 and signal.cols[0] in ldf.data_type:
            c_name = signal.cols[0]
            if ldf.data_type[c_name] == "quantitative":
                c = lux.Clause(attribute=c_name, mark_type="histogram")
            else:
                c = lux.Clause(attribute=c_name, mark_type="bar")
            clauses.append(c)

        vis_list = VisList( clauses, ldf )
    
    elif signal.f_name == "crosstab":
        ...

    elif signal.f_name == "describe":
        vis_list = VisList([lux.Clause("?", mark_type="boxplot")], ldf)
        for v in vis_list:
            v.score = 100

    elif signal.f_name == "query" or signal.f_name == "filter" or signal.f_name == "loc":
        ...

    elif signal.f_name == "groupby" or signal.f_name == "agg":
        ...
    
    else:
        if signal.cols:
            clauses = [lux.Clause(attribute=i) for i in signal.cols]
            vis_list = VisList( clauses, ldf )
    
    return vis_list
    

