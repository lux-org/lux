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
from lux.vis.CustomVis import CustomVis
from lux.implicit.ast_profiler import ColFilter

import lux
import itertools
import numpy as np
from collections import namedtuple
import altair as alt

from IPython.core.debugger import set_trace

def implicit_tab(ldf):
    """
    Generates vis based off recent implicit actions.

    Parameters
    ----------
    ldf : lux.core.frame
            LuxDataFrame with underspecified intent.

    Returns
    -------
    recommendations : Dict[str,obj]
            object with a collection of visualizations that result from the Implicit action.
    """
    most_recent_signal, col_list = lux.config.code_tracker.get_implicit_intent(id(ldf))
    str_desc = "Recommendedations based off this code: <br/>"
    lux_vis = []

    if most_recent_signal:
        lux_vis = VisList([], ldf)

        # get vis for most recent 
        vl = generate_vis_from_signal(most_recent_signal, ldf)
        if vl:
            if type(vl) == VisList:
                lux_vis._collection.extend(vl._collection)
            else: # type is list
                lux_vis._collection.extend(vl)
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

    elif signal.f_name == "subs_filter" or signal.f_name == "filter" or signal.f_name == "loc": # or query
        filts = signal.f_arg_dict["filts"]
        alt_v = plot_filter(ldf, filts)
        if alt_v:
            cv = CustomVis(alt_v)
            vis_list = [cv]

    elif signal.f_name == "groupby" or signal.f_name == "agg":
        ...
    
    else:
        if signal.cols:
            clauses = [lux.Clause(attribute=i) for i in signal.cols]
            vis_list = VisList( clauses, ldf )
    
    return vis_list
    


def plot_filter(ldf, col_filters):
    """
    data_source = df
    col_filters = [ColFilter, ...]
    """
    alt.X('Acceleration', type='quantitative'),
    alt.Y('Miles_per_Gallon', type='quantitative')

    chart = None
    if len(col_filters) == 1:
        this_filter = col_filters[0]

        x_d_type = ldf.data_type[this_filter.col_name]
        _bin = (x_d_type == "quantitative")
        
        chart = alt.Chart(ldf).mark_bar().encode(
          x= alt.X(this_filter.col_name, type=x_d_type, bin=_bin),
          y=f"count({this_filter.col_name}):Q",
          color=alt.condition(
              fill_condition(col_filters),
              alt.value("steelblue"), 
              alt.value("grey")  
          )
        )
    
    elif len(col_filters) == 3: # this looks bad when both are categorical
        x_d_type = ldf.data_type[col_filters[0].col_name]
        y_d_type = ldf.data_type[col_filters[2].col_name]
        x_bin = (x_d_type == "quantitative")
        y_bin = (y_d_type == "quantitative")
        
        chart = alt.Chart(ldf).mark_point().encode(
          x= alt.X(col_filters[0].col_name, type=x_d_type, bin=x_bin),
          y= alt.Y(col_filters[2].col_name, type=y_d_type, bin=y_bin),
          color=alt.condition(
              fill_condition(col_filters),
              alt.value("steelblue"), 
              alt.value("grey")  
          )
        )
    
    if chart:
        chart = chart.interactive()
    
    return chart

def fill_condition(conds):
    s = ""
    for c in conds:
        if type(c) == ColFilter:
            s += f"(datum['{c.col_name}'] {c.comp} '{c.val}')"
        else: # str with & or |
            s += str(c)
    return s

def compute_filter_diff(old_df, filt_df):
    """
    Assumes filt_df is a subset of old_df.
    Create indicator the size of old_df, 1= in both, 0= only in old

    TODO this still needs the columns to visualize but can be used as a flag for the color encoding
    """
    # filtered should always be smaller
    if len(filt_df) > len(old_df):
        _t = filt_df
        filt_df = old_df
        old_df = _t
    
    _d = old_df.merge(filt_df, indicator=True, how="left")

    indicator = (_d._merge == "both").astype(int)
    
    return indicator