from lux.vis.VisList import VisList
from lux.vis.Vis import Vis
from lux.vis.CustomVis import CustomVis
from lux.history.event import Event
from lux.core.frame import LuxDataFrame
import lux.utils.defaults as lux_default

import lux
import altair as alt
import random

from IPython.core.debugger import set_trace

### common utils 
tf_scale = alt.Scale(domain = [True, False], 
                    range = [lux_default.MAIN_COLOR, lux_default.BG_COLOR])


##################
# MAIN function #
##################
def generate_vis_from_signal(signal: Event, ldf: LuxDataFrame, ranked_cols=[]):
    """
    Parameters
    ----------
        signal: lux.history.Event 
            History event 
        
        ldf: lux.core.frame
            the ldf to be plotted 
    
    Returns
    -------
        chart_list: VisList OR list 
            list in event of CustomVis since cant be put into VisList directly
    """
    vis_list = []
    if signal.op_name == "value_counts" or signal.op_name == "unique":
        vis_list = process_value_counts(signal, ldf)
    
    elif signal.op_name == "crosstab":
        ...

    elif signal.op_name == "describe":
        vis_list = process_describe(signal, ldf)

    elif signal.op_name == "filter":
        vis_list = process_filter(signal, ldf)
    
    elif signal.op_name == "query" or signal.op_name == "loc": 
        vis_list = process_query_loc(signal, ldf, ranked_cols)
        
    elif signal.op_name == "groupby" or signal.op_name == "agg":
        ...
    
    elif signal.cols: # generic recs
        clauses = [lux.Clause(attribute=i) for i in signal.cols]
        vis_list = VisList( clauses, ldf )

    return vis_list

########################
# VALUE_COUNT plotting #
########################
def process_value_counts(signal, ldf):
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

    return vis_list


#####################
# DESCRIBE plotting #
#####################
def process_describe(signal, ldf):
    """
    Plots boxplots of either parent df if this is the describe df or of this df

    Parameters
    ----------
        signal: lux.history.Event 
            History event that is a FILTER
        
        ldf: lux.core.frame
            the ldf to be plotted 
    
    Returns
    -------
        chart_list: VisList 
    """
    # if ldf is df returned by describe plot the parent of ldf
    if (ldf._parent_df is not None and 
        all(ldf.index == ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max'])):
        
        vl = VisList([lux.Clause("?", mark_type="boxplot")], ldf._parent_df)

    # or the full df?
    else:
        vl = VisList([lux.Clause("?", mark_type="boxplot")], ldf)
    
    # hack to get vis to appear at the front 
    for v in vl:
        v.score = 100
    
    return vl

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
        chart_list: VisList or empty array
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

    # turn into vislist 
    vis_list = []
    if chart_list:
        for _v in chart_list:
            vis_list.append( CustomVis(_v) )

    return vis_list

def process_query_loc(signal, ldf, ranked_cols):
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
        chart_list: VisList or empty array
    """
    filt_type = signal.kwargs["filt_type"]
    query_df = signal.kwargs["query_df"]
    plot_df = None 
    chart_list = None

    # TODO.. which columns should I plot?

    # get parent df to plot and filter mask
    if filt_type == "parent" and query_df is not None:
        mask, diff_cols = compute_filter_diff(ldf, query_df)
        plot_df = ldf
        plot_cols = get_query_cols(ranked_cols, diff_cols)

        # get charts
        chart_list = [plot_filter(plot_df, plot_cols, mask)]
    
    elif filt_type == "child" and ldf._parent_df is not None:
        mask, diff_cols = compute_filter_diff(ldf._parent_df, ldf)
        plot_df = ldf._parent_df
        plot_cols = get_query_cols(ranked_cols, diff_cols)

        # get charts
        chart_list = [plot_filter(plot_df, plot_cols, mask)]
        chart_list.append(plot_filter_count(plot_df, mask))
    
    # turn into vislist 
    vis_list = []
    if chart_list:
        for _v in chart_list:
            vis_list.append( CustomVis(_v) )

    return vis_list

def get_query_cols(ranked_cols, diff_cols):
    """
    Params: both should be lists of col names, or empty list
    """
    if ranked_cols:
        return ranked_cols 
    
    return random.sample(diff_cols, 2) # randomly select here for funsies


def plot_filter_count(ldf, mask):
    """
    For filtered dfs, plot the count of columns compared to count of unfiltered df

    Parameters
    ----------
        ldf: lux.core.LuxDataFrame 
            parent ldf that was filtered
        
        mask: boolean list or series
            True if in filter, False if not
    
    Returns
    -------
        chart: Altair chart
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


def plot_filter(ldf, cols, mask, card_thresh=12):
    """
    Plot 1d or 2d plot of filted df

    Parameters
    ----------
        ldf: lux.core.LuxDataFrame 
            parent ldf that was filtered
        
        cols: list 
            which col(s) should be in the plot 

        mask: boolean list or series
            True if in filter, False if not
    
    Returns
    -------
        chart: Altair chart
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
    
    elif len(cols) >= 2 and (cols[0] in ldf.data_type) and (cols[1] in ldf.data_type):
        
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

        x_title = f"{x_var}"
        y_title = f"{y_var}"
        # filter for cardinality if high cardinality nominal vars
        if x_d_type == "nominal" and ldf.cardinality[x_var] > card_thresh:
            _most_common = ldf[x_var].value_counts()[:card_thresh].index
            ldf = ldf[ldf[x_var].isin(_most_common)]
            x_title += f" (top {card_thresh})"
        
        if y_d_type == "nominal" and ldf.cardinality[y_var] > card_thresh:
            _most_common = ldf[y_var].value_counts()[:card_thresh].index
            ldf = ldf[ldf[y_var].isin(_most_common)]
            y_title += f" (top {card_thresh})"

        
        bg = alt.Chart(ldf) \
                .mark_circle(color = lux_default.BG_COLOR) \
                .encode(
                    x= alt.X(x_var, type=x_d_type, bin=x_bin, title=x_title),
                    y= alt.Y(y_var, type=y_d_type, bin=y_bin, title=y_title),
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


def compute_filter_diff(old_df, filt_df):
    """
    Assumes filt_df is a subset of old_df. Creates indicator the size of the larger df
    
    True = in both, False = only in larger
    """
    old_df = old_df.copy()
    filt_df = filt_df.copy()
    # filtered should always be smaller
    if len(filt_df) > len(old_df):
        _t = filt_df
        filt_df = old_df
        old_df = _t
    
    _d = old_df.merge(filt_df, indicator=True, how="left")
    indicator = (_d._merge == "both") #.astype(int)

    # which cols change? this isnt very informative since 
    # many columns change other than the filter. TODO change this 
    different_cols = list(old_df.columns[old_df.nunique() != filt_df.nunique()])
    
    return indicator, different_cols