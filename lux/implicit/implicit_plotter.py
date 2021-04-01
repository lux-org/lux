from lux.vis.VisList import VisList
from lux.vis.Vis import Vis
from lux.vis.CustomVis import CustomVis
from lux.history.event import Event
from lux.core.frame import LuxDataFrame
import lux.utils.defaults as lux_default

from lux.implicit import cg_plotter

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
        used_cols: list
            which columns were used in the returned vis(i)
    """
    vis_list = []
    used_cols = []
    if signal.op_name == "value_counts" or signal.op_name == "unique":
        vis_list, used_cols = process_value_counts(signal, ldf)
    
    elif signal.op_name == "describe":
        vis_list, used_cols = process_describe(signal, ldf)

    elif signal.op_name == "filter":
        vis_list, used_cols = process_filter(signal, ldf, ranked_cols)
    
    elif signal.op_name == "query" or signal.op_name == "slice": 
        vis_list, used_cols = process_query_loc(signal, ldf, ranked_cols)

    # elif signal.op_name == "crosstab":
    #     ...
 
    # elif signal.op_name == "groupby" or signal.op_name == "agg": # gb is handled in cg_plotter.py
    #     ...
    
    elif signal.cols: # generic recs
        clauses = [lux.Clause(attribute=i) for i in signal.cols]
        used_cols = signal.cols
        vis_list = VisList( clauses, ldf )
    
    return vis_list, used_cols

########################
# VALUE_COUNT plotting #
########################
def process_value_counts(signal, ldf):
    """
    Generate 1d distribution plot either from raw data (if parent and unaggregated)
    or from child 

    Returns
    -------
        vis_list: VisList 
            with the vis 
        array: []
            which columns were used 
    """
    try: 
        rank_type = signal.kwargs["rank_type"]
        c_name = signal.cols[0]
        if rank_type == "parent" and not ldf.pre_aggregated:
            if ldf.data_type[c_name] == "quantitative":
                clse = lux.Clause(attribute=c_name, mark_type="histogram")
            else:
                clse = lux.Clause(attribute=c_name, mark_type="bar")
            
            vis_list = VisList([clse], ldf )

        else: # "child" AND ldf is pre_aggregated
            # v = cg_plotter.plot_col_vis(c_name, "Count")
            
            # make vis consistent with normal histogram from history
            v = Vis(
                [
                    lux.Clause(
                        attribute=c_name,
                        data_type="nominal",
                        data_model="dimension",
                        aggregation="",
                        channel="x",
                    ),
                    lux.Clause(
                        attribute="Number of Records",
                        data_type="quantitative",
                        data_model="measure",
                        aggregation=None,
                        channel="y",

                    ),
                ]
            )
            flat = ldf.reset_index()
            flat = flat.rename(columns={"index": c_name, c_name: "Number of Records"})
            vis_list = VisList([v], flat)
        
        return vis_list, [c_name]
    
    except (IndexError, KeyError):
        return VisList( [], ldf ), []


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
        array: []
            which columns were used 
            NOTE: this is intentionally wrong here bc want to still use these cols elsewhere 
            since will not be boxplots elsewhere
    """
    # set_trace()
    # if ldf is df returned by describe plot the parent of ldf
    if (ldf._parent_df is not None and len(ldf) == 8 and
        all(ldf.index == ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']) ):
        
        vl = VisList([lux.Clause("?", mark_type="boxplot")], ldf._parent_df)

    # or the full df?
    else:
        vl = VisList([lux.Clause("?", mark_type="boxplot")], ldf)
    
    # hack to get vis to appear at the front 
    # for v in vl:
    #     v.score = 100
    
    return vl, []

###################
# FILTER plotting #
###################
def process_filter(signal, ldf, ranked_cols):
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
        cols: []
            which columns were used 
    """
    rank_type = signal.kwargs["rank_type"]
    parent_mask = signal.kwargs["filt_key"]

    # cols from same execution time may have been in filter so we DONT want to use them
    ex_time = signal.ex_count
    other_signals = ldf._history.filter_by_ex_time(ex_time)
    exclude_cols = set()
    for s in other_signals:
        exclude_cols.update(s.cols)
    
    # set_trace()
    col_combos = get_col_recs(ldf, ranked_cols, exclude_cols)

    all_used_cols = set()
    chart_list = []
    
    plot_df = None
    if rank_type == "parent":
        plot_df = ldf
    elif ldf._parent_df is not None: # rank_type == "child"
        plot_df = ldf._parent_df
        chart_list.append(plot_filter_count(ldf._parent_df, parent_mask)) # count 

    if plot_df is not None:
        for input_combo in col_combos:
            _v = plot_filter(plot_df, input_combo, parent_mask)
            all_used_cols.update(input_combo)
            chart_list.append(_v)

    # turn into vislist 
    # vis_list = []
    # if chart_list:
    #     for _v in chart_list:
    #         vis_list.append( CustomVis(_v) )

    return chart_list, list(all_used_cols)

def get_col_recs(ldf, ranked_cols, exclude=[]):
    # sets for easy comparision
    all_c = set(ldf.columns)
    ranked_cols = set(ranked_cols)
    exclude = set(exclude)

    good_c = all_c - exclude # all cols not in exclude
    good_ranked = ranked_cols - exclude
    col_tups_single = set()
    final = []
    
    # look at interesting columns individually
    for c in good_ranked:
        col_tups_single.add(c)
    
    quant_cols = set()
    cat_cols = set()
    for c in good_c:
        if ldf.data_type[c] == "temporal":
            col_tups_single.add(c)
        elif ldf.data_type[c] == "quantitative":
            quant_cols.add(c)
        elif ldf.data_type[c] == "nominal":
            cat_cols.add(c)
    
    if all( [ ldf.data_type[c] == "quantitative" for c in exclude ] ): # filter is quant 
        for item in cat_cols:
            col_tups_single.add(item)
    elif all( [ ldf.data_type[c] == "nominal" for c in exclude ] ): # filter is categorical
        for item in quant_cols:
            col_tups_single.add(item)
    else:
        # use all quant categorical combos
        for q in quant_cols:
            for n in cat_cols:
                final.append([q, n]) 
    
    for i in col_tups_single: final.append([i])

    return final


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
        plot_cols: array
            which cols were used
    
    # TODO this could prob be combined with process_filter 
    """
    rank_type = signal.kwargs["rank_type"]
    child_df = signal.kwargs["child_df"]

    p_df, c_df = None, None
    chart_list = []
    if rank_type == "parent" and child_df is not None:
        p_df = ldf
        c_df = child_df
    elif rank_type == "child" and ldf._parent_df is not None:
        p_df = ldf._parent_df
        c_df = ldf
    
    mask, same_cols = compute_filter_diff(p_df, c_df)
    # set_trace()
    col_combos = get_col_recs(ldf, ranked_cols, same_cols) # TODO this excludes same cols is that good?

    all_used_cols = set()
    if rank_type == "child": 
        chart_list.append(plot_filter_count(p_df, mask))
    if p_df is not None:
        for input_combo in col_combos:
            _v = plot_filter(p_df, input_combo, mask)
            all_used_cols.update(input_combo)
            chart_list.append(_v)
    
    # turn into vislist 
    # vis_list = []
    # if chart_list:
    #     for _v in chart_list:
    #         vis_list.append( CustomVis(_v) )

    return chart_list, list(all_used_cols)

# def get_query_cols(ranked_cols, diff_cols):
#     """
#     Params: both should be lists of col names, or empty list
#     """
#     if ranked_cols:
#         return ranked_cols 
    
#     return random.sample(diff_cols, 2) # randomly select here for funsies


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
        chart: CustomVis chart
    """

    ldf = ldf.copy()
    ldf["filt_mask"] = mask

    chart = alt.Chart(ldf).mark_bar(size=75).encode(
        y = alt.Y("count()", title="Filtered Data Count"),
        color = alt.Color("filt_mask", 
                           scale = tf_scale,
                           legend = None),
        order=alt.Order('filt_mask', sort='descending') # make sure stack goes True then False for filter
        )
    
    # DONT use interactive for this chart, it breaks for some reason

    v = CustomVis(chart, width=90)

    return v 


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
        chart: CustomVis chart
    """
    ldf = ldf.copy()
    ldf["filt_mask"] = mask

    chart = None
    
    if len(cols) == 1 and cols[0] in ldf.data_type:
        x_var = cols[0]
        x_title = f"{x_var}"
        x_d_type = ldf.data_type[x_var]
        _bin = (x_d_type == "quantitative")

        filt_text = None
        if x_d_type == "nominal" and ldf.cardinality[x_var] > card_thresh:
            vc = ldf[x_var].value_counts()
            _most_common = vc.iloc[:card_thresh].index
            ldf = ldf[ldf[x_var].isin(_most_common)]
            x_title += f" (top {card_thresh})"
            filt_text = f"+ {len(vc) - card_thresh} more..." 

        
        chart = alt.Chart(ldf).mark_bar().encode(
          x= alt.X(x_var, type=x_d_type, bin=_bin, title=x_title),
          y=f"count({x_var}):Q",
          color= alt.Color("filt_mask", scale= tf_scale, title="Is Filtered?" )
        )

        if filt_text:
            filt_label = alt.Chart(ldf).mark_text(
                x=155,
                y=142,
                align="right",
                color="#ff8e04",
                fontSize=11,
                text= filt_text,
            )

            chart = chart + filt_label
    
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

        filt_text_x = None
        # filt_text_y = None
        # filter for cardinality if high cardinality nominal vars
        if x_d_type == "nominal" and ldf.cardinality[x_var] > card_thresh:
            vc = ldf[x_var].value_counts()
            _most_common = vc.iloc[:card_thresh].index
            ldf = ldf[ldf[x_var].isin(_most_common)]
            x_title += f" (top {card_thresh})"
            filt_text_x = f"+ {len(vc) - card_thresh} more..."
        
        if y_d_type == "nominal" and ldf.cardinality[y_var] > card_thresh:
            vc = ldf[y_var].value_counts()
            _most_common = vc.iloc[:card_thresh].index
            ldf = ldf[ldf[y_var].isin(_most_common)]
            y_title += f" (top {card_thresh}/{len(vc)}...)"
            # filt_text_y = f"+ {len(vc) - card_thresh} more..." # TODO what if x and y are high card
        
        
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

        if filt_text_x:
            filt_c = alt.Chart(ldf).mark_text(
                x=155,
                y=142,
                align="right",
                color="#ff8e04",
                fontSize=11,
                text= filt_text_x,
            )

            chart = chart + filt_c
        
        # if filt_text_y:
        #     filt_c = alt.Chart(ldf).mark_text(
        #         x=15,
        #         y=135,
        #         align="right",
        #         color="#ff8e04",
        #         fontSize=11,
        #         text= filt_text_y,
        #     )

        #     chart = chart + filt_c
            
    
    if chart:
        chart = chart.interactive()

    v = CustomVis(chart)
    
    return v


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
    same_cols = list(old_df.columns[old_df.nunique() == filt_df.nunique()])
    
    return indicator, same_cols