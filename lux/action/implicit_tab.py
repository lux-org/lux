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
from lux.history.event import Event
from lux.core.frame import LuxDataFrame

import lux
import altair as alt

from IPython.core.debugger import set_trace

def implicit_tab(ldf: LuxDataFrame):
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
    # these events are cleansed when fetched 
    # set_trace()
    most_recent_event, col_list = ldf.history.get_implicit_intent(ldf.columns)
    str_desc = "Recommendedations based off code containing: <br/>"
    lux_vis = []

    # get unique vis for recent col ref 
    if most_recent_event:
        lux_vis = VisList([], ldf)
        vl = generate_vis_from_signal(most_recent_event, ldf)
        
        if vl:
            if type(vl) == VisList:
                lux_vis._collection.extend(vl._collection)
            else: # type is list
                lux_vis._collection.extend(vl)
            str_desc += f"> {most_recent_event.op_name} <br/>"
        
    # get multiple vis for col refs
    if col_list:
        col_vis_l = []
        #max_score = len(col_vis_l)
        for i, c in enumerate(col_list):
            col_v = Vis( [lux.Clause(c)] )
            #col_v.score = max_score - i
            col_vis_l.append(col_v)
            str_desc += f"> Reference to attribute {c} <br/>"
            
        vl_2 = VisList(col_vis_l, ldf)

        if lux_vis:
            lux_vis._collection.extend(vl_2._collection)
        else:
            lux_vis = vl_2
        
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

# def validate_history(most_recent_event, col_list, ldf: LuxDataFrame)

def generate_vis_from_signal(signal: Event, ldf: LuxDataFrame):
    """
    Generate custom vis for this event type from ldf
    """
    vis_list = []
    if signal.op_name == "value_counts" or signal.op_name == "unique":
        
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
    
    elif signal.op_name == "crosstab":
        ...

    elif signal.op_name == "describe":
        vis_list = VisList([lux.Clause("?", mark_type="boxplot")], ldf)
        for v in vis_list:
            v.score = 100

    elif signal.op_name == "filter": #or signal.op_name == "loc": # or query
        alt_v = process_filter(signal, ldf)
        if alt_v:
            cv = CustomVis(alt_v)
            vis_list = [cv]
        
    elif signal.op_name == "groupby" or signal.op_name == "agg":
        ...
    
    else:
        if signal.cols:
            clauses = [lux.Clause(attribute=i) for i in signal.cols]
            vis_list = VisList( clauses, ldf )
    
    return vis_list
    

def process_filter(signal, ldf):
    filt_type = signal.kwargs["filt_type"]
    parent_mask = signal.kwargs["filt_key"]

    # get columns of interest 
    ex_time = signal.ex_count

    other_signals = ldf._history.filter_by_ex_time(ex_time)
    cols = set()
    for s in other_signals:
        cols.update(s.cols)

    cols = list(cols)
    
    chart = None
    if len(cols): # if no columns captured in same time we wont plot
        if filt_type == "parent":
            chart = plot_filter(ldf, cols, parent_mask)
        
        elif ldf._parent_df is not None: # filt_type == "child"
            chart = plot_filter(ldf._parent_df, cols, parent_mask)

    return chart



def plot_filter(ldf, cols, mask):
    """
    data_source = df
    col_filters = [ColFilter, ...]
    """
    ldf = ldf.copy()
    ldf["filt_mask"] = mask

    chart = None

    tf_scale = alt.Scale(domain=[True, False], range=["steelblue", "grey"])
    
    if len(cols) == 1:
        this_col = cols[0]

        x_d_type = ldf.data_type[this_col]
        _bin = (x_d_type == "quantitative")
        
        chart = alt.Chart(ldf).mark_bar().encode(
          x= alt.X(this_col, type=x_d_type, bin=_bin),
          y=f"count({this_col}):Q",
          color= alt.Color("filt_mask", scale= tf_scale )
        )
    
    elif len(cols) >= 2: # this looks bad when both are categorical
        x_d_type = ldf.data_type[cols[0]]
        y_d_type = ldf.data_type[cols[1]]
        x_bin = (x_d_type == "quantitative")
        y_bin = (y_d_type == "quantitative")
        
        chart = alt.Chart(ldf).mark_point().encode(
          x= alt.X(cols[0], type=x_d_type, bin=x_bin),
          y= alt.Y(cols[1], type=y_d_type, bin=y_bin),
          color= alt.Color("filt_mask", scale= tf_scale )
        )
    
    if chart:
        chart = chart.interactive()
    
    return chart


# def compute_filter_diff(old_df, filt_df):
#     """
#     Assumes filt_df is a subset of old_df.
#     Create indicator the size of old_df, 1= in both, 0= only in old
#     """
#     # filtered should always be smaller
#     if len(filt_df) > len(old_df):
#         _t = filt_df
#         filt_df = old_df
#         old_df = _t
    
#     _d = old_df.merge(filt_df, indicator=True, how="left")

#     indicator = (_d._merge == "both").astype(int)
    
#     return indicator