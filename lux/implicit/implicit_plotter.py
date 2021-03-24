from lux.vis.VisList import VisList
from lux.vis.Vis import Vis
from lux.vis.CustomVis import CustomVis
from lux.history.event import Event
from lux.core.frame import LuxDataFrame
import lux.utils.defaults as lux_default

import lux
import altair as alt

from IPython.core.debugger import set_trace

### common utils 
tf_scale = alt.Scale(domain = [True, False], 
                    range = [lux_default.MAIN_COLOR, lux_default.BG_COLOR])


##################
# MAIN function #
##################
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
        alt_v_list = process_filter(signal, ldf)
        if alt_v_list:
            for _v in alt_v_list:
                vis_list.append( CustomVis(_v) )
        
    elif signal.op_name == "groupby" or signal.op_name == "agg":
        ...
    
    else:
        if signal.cols:
            clauses = [lux.Clause(attribute=i) for i in signal.cols]
            vis_list = VisList( clauses, ldf )
    
    return vis_list

###################
# FILTER plotting #
###################
def process_filter(signal, ldf):
    """
    Decides if plotting parent that WAS filtered, or the resulting df
    FROM a filter and plots accordingly.

    Parameters
    ----------
        signal: lux.history.Event 
            History event that is a FILTER
        
        ldf: lux.core.frame
            the ldf to be plotted 
    
    Returns
    -------
        chart_list: list
    """
    filt_type = signal.kwargs["filt_type"]
    parent_mask = signal.kwargs["filt_key"]

    # get columns of interest from same execution time
    ex_time = signal.ex_count
    other_signals = ldf._history.filter_by_ex_time(ex_time)
    cols = set()
    for s in other_signals:
        cols.update(s.cols)
    cols = list(cols)
    
    # get vis
    chart_list = None
    if len(cols): # if no columns captured in same time we wont plot
        if filt_type == "parent":
            chart_list = [plot_filter(ldf, cols, parent_mask)]
        
        elif ldf._parent_df is not None: # filt_type == "child"
            chart_list = [plot_filter(ldf._parent_df, cols, parent_mask)]
            chart_list.append(plot_filter_count(ldf._parent_df, parent_mask))

    return chart_list


def plot_filter_count(ldf, mask):
    """
    For filtered dfs, plot the count of columns compared to count of unfiltered df
    """

    ldf = ldf.copy()
    ldf["filt_mask"] = mask

    chart = alt.Chart(ldf).mark_bar(size=75).encode(
        x = alt.X("count()", title="Filtered Data Count"),
        color = alt.Color("filt_mask", 
                           scale = tf_scale,
                           legend = None),
        order=alt.Order('filt_mask', sort='descending') # make sure stack goes True then False for filter
        )
    
    # DONT use interactive for this chart, it breaks for some reason

    return chart 


def plot_filter(ldf, cols, mask):
    """
    data_source = df
    col_filters = [ColFilter, ...]
    """
    ldf = ldf.copy()
    ldf["filt_mask"] = mask

    chart = None
    
    if len(cols) == 1 and cols[0] in ldf.data_type:
        this_col = cols[0]

        x_d_type = ldf.data_type[this_col]
        _bin = (x_d_type == "quantitative")
        
        chart = alt.Chart(ldf).mark_bar().encode(
          x= alt.X(this_col, type=x_d_type, bin=_bin),
          y=f"count({this_col}):Q",
          color= alt.Color("filt_mask", scale= tf_scale, title="Is Filtered?" )
        )
    
    elif len(cols) >= 2 and (cols[0] in ldf.data_type) and (cols[1] in ldf.data_type): # this looks bad when both are categorical
        
        # set x as quant if possible
        if ldf.data_type[cols[0]] == "quantitative":
            x_var = cols[0]
            y_var = cols[1]
        else:
            x_var = cols[1]
            y_var = cols[0]

        
        x_d_type = ldf.data_type[x_var]
        y_d_type = ldf.data_type[y_var]
        x_bin = (x_d_type == "quantitative")
        y_bin = (y_d_type == "quantitative")
        
        bg = alt.Chart(ldf) \
                .mark_circle(color = lux_default.BG_COLOR) \
                .encode(
                    x= alt.X(x_var, type=x_d_type, bin=x_bin),
                    y= alt.Y(y_var, type=y_d_type, bin=y_bin),
                    size=alt.Size("count()", legend=None),
                )
        
        filt_chart = alt.Chart(ldf) \
                        .mark_circle(color = lux_default.MAIN_COLOR) \
                        .transform_filter( (alt.datum.filt_mask == True)) \
                        .encode(
                            x= alt.X(x_var, type=x_d_type, bin=x_bin),
                            y= alt.Y(y_var, type=y_d_type, bin=y_bin),
                            size=alt.Size("count()", legend=None),
                        )
        
        chart = bg + filt_chart
    
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