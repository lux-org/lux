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

from sklearn.preprocessing import LabelEncoder
from pyemd import emd_samples


from IPython.core.debugger import set_trace

### common utils and settings
tf_scale = alt.Scale(domain=[True, False], range=[lux_default.MAIN_COLOR, lux_default.BG_COLOR])

PLOT_CARD_THRESH = 12

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
        chart_list: VisList
            VistList of returned vis
        used_cols: list
            which columns were used in the returned vis(i)
    """
    ldf.history.freeze()
    vis_list = VisList([])
    used_cols = []
    if signal.op_name == "value_counts" or signal.op_name == "unique":
        vis_list, used_cols = process_value_counts(signal, ldf)

    elif signal.op_name == "describe":
        vis_list, used_cols = process_describe(signal, ldf)

    elif (
        signal.op_name == "filter"
        or signal.op_name == "query"
        or signal.op_name == "slice"
        or signal.op_name == "gb_filter"
    ):

        vis_list, used_cols = process_filter(signal, ldf, ranked_cols)

    elif signal.op_name == "dropna":
        vis_list, used_cols = process_filter(signal, ldf, ranked_cols)

    elif signal.op_name == "isna" or signal.op_name == "notnull":
        vis_list, used_cols = process_null_plot(signal, ldf)

    elif signal.cols:  # generic recs
        vis_list, used_cols = process_generic(signal, ldf)

    ldf.history.unfreeze()

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

            vis_list = VisList([clse], ldf)

        else:  # "child" AND ldf is pre_aggregated
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
        return VisList([], ldf), []


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
            Empty array of used cols so not excluded in other vis
    """
    if (
        ldf._parent_df is not None
        and len(ldf) == 8
        and all(ldf.index == ["count", "mean", "std", "min", "25%", "50%", "75%", "max"])
    ):
        plot_df = ldf._parent_df
    else:
        plot_df = ldf

    collection = []

    for c in signal.cols:
        v = Vis([lux.Clause(c, mark_type="boxplot")], plot_df)
        collection.append(v)

    vl = VisList(collection)

    return vl, []


###################
# FILTER plotting #
###################
def process_filter(signal, ldf, ranked_cols, num_vis_cap=5):
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


    """
    rank_type = signal.kwargs.get("rank_type", None)
    child_df = signal.kwargs.get("child_df", None)
    parent_mask = signal.kwargs.get("filt_key", None)

    # assign parent and child
    p_df, c_df = None, None
    if rank_type == "parent" and child_df is not None:
        p_df = ldf
        c_df = child_df
    elif rank_type == "child" and ldf._parent_df is not None:
        if isinstance(ldf._parent_df, lux.core.groupby.LuxGroupBy):
            p_df = ldf._parent_df._parent_df
        else:
            p_df = ldf._parent_df
        c_df = ldf

    # get mask
    if parent_mask is not None:
        mask = parent_mask
    else:
        mask, same_cols = compute_filter_diff(p_df, c_df)

    # get cols with large dist change
    vis_cols = get_col_recs(p_df, c_df)

    # populate vis
    all_used_cols = set()
    chart_list = []
    if rank_type == "child":
        chart_list.append(plot_filter_count(p_df, mask))

    if p_df is not None:
        for c in vis_cols[:num_vis_cap]:
            _v = plot_filter(p_df, [c], mask)
            chart_list.append(_v)
            all_used_cols.add(c)

    vl = VisList(chart_list)

    return vl, list(all_used_cols)


def get_col_recs(parent_df, child_df):
    """
    Look at each column and calculate distance metric by column
    """
    dists = []
    parent_df.history.freeze()
    child_df.history.freeze()

    # TODO store this on the df so dont have to recalc so much
    # TODO calc distance for 2d as well
    for c in parent_df.columns:
        p_data = parent_df[c].dropna().values
        c_data = child_df[c].dropna().values

        if parent_df.data_type[c] != "quantitative" and parent_df.cardinality[c] > PLOT_CARD_THRESH:
            dist = -1
        else:
            dist = calc_dist_distance(p_data, c_data, parent_df.data_type[c])

        if dist != -1:
            dists.append((c, dist))

    dists.sort(key=lambda x: x[1], reverse=True)
    col_order = [i[0] for i in dists]

    parent_df.history.unfreeze()
    child_df.history.unfreeze()

    return col_order


def calc_dist_distance(p_data, c_data, dtype):
    """
    Calculate wasserstein / earth movers distance between two samples.
    c_data must be subset of p_data
    """
    try:
        if dtype == "nominal":
            le = LabelEncoder()
            le.fit(p_data)
            p_data = le.transform(p_data)
            c_data = le.transform(c_data)
        return emd_samples(p_data, c_data)
    except Exception:
        return -1


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
    indicator = _d._merge == "both"  # .astype(int)

    # which cols change? this isnt very informative since
    # many columns change other than the filter.
    same_cols = list(old_df.columns[old_df.nunique() == filt_df.nunique()])

    return indicator, same_cols


def plot_filter_count(ldf, mask, c_col_name="In filter?", c_title="Filtered Data Count"):
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
    ldf[c_col_name] = mask

    chart = (
        alt.Chart(ldf)
        .mark_bar(size=75)
        .encode(
            y=alt.Y("count()", title=c_title),
            color=alt.Color(c_col_name, scale=tf_scale, legend=None),
            order=alt.Order(
                c_col_name, sort="descending"
            ),  # make sure stack goes True then False for filter
        )
    )

    # DONT use interactive for this chart, it breaks bc ordinal scale I think
    intent = []  # NOTE: this isnt great intent for this chart
    cv = CustomVis(intent, chart, ldf, width=90, override_c_config={"interactive": False})

    return cv


def plot_filter(ldf, cols, mask, card_thresh=PLOT_CARD_THRESH, filt_frac_thresh=0.1):
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

    # make sure filtered data is at least 10% of dataset, if not only use filter
    n = len(ldf)
    filt_df_true = ldf[mask]
    filt_n = len(filt_df_true)

    if (filt_n / n) < filt_frac_thresh:
        ldf = filt_df_true

    chart = None
    intent = []

    if len(cols) == 1 and cols[0] in ldf.data_type:
        x_var = cols[0]
        x_title = f"{x_var}"
        x_d_type = ldf.data_type[x_var]
        _bin = x_d_type == "quantitative"

        filt_text = None
        if x_d_type == "nominal":
            if ldf.cardinality[x_var] > card_thresh:
                vc = filt_df_true[x_var].value_counts()
                _most_common = vc.iloc[:card_thresh].index
                ldf = ldf[ldf[x_var].isin(_most_common)]
                x_title += f" (top {card_thresh})"
                filt_text = f"+ {len(vc) - card_thresh} more..."
            alt_x_enc = alt.X(x_var, type=x_d_type, bin=_bin, title=x_title, sort="-y")
        else:
            alt_x_enc = alt.X(x_var, type=x_d_type, bin=_bin, title=x_title)

        chart = (
            alt.Chart(ldf)
            .mark_bar()
            .encode(
                x=alt_x_enc,
                y=f"count({x_var}):Q",
                color=alt.Color("filt_mask", scale=tf_scale, title="Is Filtered?"),
            )
        )

        intent = [lux.Clause(x_var, data_type=x_d_type)]

        if filt_text:
            filt_label = alt.Chart(ldf).mark_text(
                x=155,
                y=142,
                align="right",
                color="#ff8e04",
                fontSize=11,
                text=filt_text,
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
        x_bin = x_d_type == "quantitative"
        y_bin = y_d_type == "quantitative"

        x_title = f"{x_var}"
        y_title = f"{y_var}"

        filt_text_x = None
        # filt_text_y = None
        # filter for cardinality if high cardinality nominal vars
        if x_d_type == "nominal" and ldf.cardinality[x_var] > card_thresh:
            vc = filt_df_true[x_var].value_counts()
            _most_common = vc.iloc[:card_thresh].index
            ldf = ldf[ldf[x_var].isin(_most_common)]
            x_title += f" (top {card_thresh})"
            filt_text_x = f"+ {len(vc) - card_thresh} more..."

        if y_d_type == "nominal" and ldf.cardinality[y_var] > card_thresh:
            vc = filt_df_true[y_var].value_counts()
            _most_common = vc.iloc[:card_thresh].index
            ldf = ldf[ldf[y_var].isin(_most_common)]
            y_title += f" (top {card_thresh}/{len(vc)}...)"
            # filt_text_y = f"+ {len(vc) - card_thresh} more..." # TODO what if x and y are high card

        bg = (
            alt.Chart(ldf)
            .mark_circle(color=lux_default.BG_COLOR)
            .encode(
                x=alt.X(x_var, type=x_d_type, bin=x_bin, title=x_title),
                y=alt.Y(y_var, type=y_d_type, bin=y_bin, title=y_title),
                size=alt.Size("count()", legend=None),
            )
        )

        filt_chart = (
            alt.Chart(ldf)
            .mark_circle(color=lux_default.MAIN_COLOR)
            .transform_filter((alt.datum.filt_mask == True))
            .encode(
                x=alt.X(x_var, type=x_d_type, bin=x_bin),
                y=alt.Y(y_var, type=y_d_type, bin=y_bin),
                size=alt.Size("count()", legend=None),
            )
        )

        chart = bg + filt_chart

        intent = [lux.Clause(x_var, data_type=x_d_type), lux.Clause(y_var, data_type=y_d_type)]

        if filt_text_x:
            filt_c = alt.Chart(ldf).mark_text(
                x=155,
                y=142,
                align="right",
                color="#ff8e04",
                fontSize=11,
                text=filt_text_x,
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

    cv = CustomVis(intent, chart, ldf)

    return cv


######################
# Null df plotting   #
######################
def process_null_plot(signal, ldf):
    """
    Generate count histograms of df if boolean showing isna
    """
    rank_type = signal.kwargs.get("rank_type", None)

    chart_list = []

    if rank_type == "child" and all(ldf.dtypes == "bool"):

        for c in ldf.columns:
            chart = plot_na_count(ldf, c, f"{c} {signal.op_name}")
            chart_list.append(chart)

    vl = VisList(chart_list)

    return vl, []


def plot_na_count(ldf, c_col_name, c_title):
    """
    For count dfs, plot the count of columns compared to count of unfiltered df

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
    chart = (
        alt.Chart(ldf)
        .mark_bar(size=75)
        .encode(
            y=alt.Y("count()", title=c_title),
            color=alt.Color(c_col_name, scale=tf_scale, legend=None),
            order=alt.Order(
                c_col_name, sort="descending"
            ),  # make sure stack goes True then False for filter
        )
    )

    # DONT use interactive for this chart, it breaks bc ordinal scale I think
    intent = [c_col_name]
    cv = CustomVis(intent, chart, ldf, width=90, override_c_config={"interactive": False})

    return cv


######################
# GENERIC plotting   #
######################
def process_generic(signal, ldf):
    vl = []

    for c in signal.cols:
        v = Vis([lux.Clause(attribute=c)])
        vl.append(v)

    used_cols = signal.cols
    vis_list = VisList(vl, ldf)

    return vis_list, used_cols
