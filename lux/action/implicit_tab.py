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
    signals_ranked = lux.config.code_tracker.get_implicit_intent("df")
    str_desc = "Recommendedations based off this code: <br/>"

    if signals_ranked:
        lux_vis = VisList([], ldf)

        for i, s in enumerate(signals_ranked):
            vl = generate_vis_from_signal(s, ldf)
            
            if vl:
                lux_vis._collection.extend(vl._collection)

            str_desc += f"[{i}] {s.code_str} <br/>"
        
        #lux_vis.refresh_source(ldf)

    
    else:
        lux_vis = []

    numeric_cols = list(ldf.select_dtypes(include= np.number).columns)
    
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

    elif signal.f_name == "query" or signal.f_name == "filter" or signal.f_name == "loc":
        ...

    elif signal.f_name == "groupby" or signal.f_name == "agg":
        ...
    
    else:
        if signal.cols:
            clauses = [lux.Clause(attribute=i) for i in signal.cols]
            vis_list = VisList( clauses, ldf )
    
    return vis_list
    

