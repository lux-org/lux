import lux
from lux.vis.CustomVis import CustomVis
from lux.vis.Vis import Vis

import altair as alt

##################
# Plotting funcs #
##################
def plot_col_vis(index_column_name, attribute):
    """
    Normal vis for column groups with ordinal on y and quant on x
    """
    vis = Vis(
        [
            lux.Clause(
                attribute=index_column_name,
                data_type="nominal",
                data_model="dimension",
                aggregation="",
            ),
            lux.Clause(
                attribute=attribute,
                data_type="quantitative",
                data_model="measure",
                aggregation=None,
            ),
        ]
    )
    return vis


def plot_std_bar(df, attribute):
    """
    In:
        df: results of df.std() (as a dataframe) after converting Timedelta object to float64 (in days)
        attribute: the column name where df.std() is stored

    Returns:
        CustomVis of this object
    """
    df = df.reset_index()

    x_name = attribute
    y_name = "index"

    v = (
        alt.Chart(df)
        .mark_bar()
        .encode(x=alt.X(x_name, type="quantitative"), y=alt.Y(y_name, type="nominal"))
    )

    intent = [
        lux.Clause(x_name, data_type="quantitative", data_model="measure"),
        lux.Clause(y_name, data_type="nominal", data_model="dimension"),
    ]

    cv = CustomVis(intent, v, df)
    cv.mark = "bar"
    return cv


def plot_gb_mean_errorbar(df_m, df_s):
    """
    In:
        df_m: results of df.groupby().mean() renamed to have mean in col names
        df_s: result of df.groupby().std() renamed to have std in col names

    Returns:
        list of CustomVis objects
    """
    # tog = df_m.join(df_s, lsuffix=" (mean)", rsuffix=" (std)").reset_index()
    tog = df_m.join(df_s).reset_index()
    index_col = tog.columns[0]
    vl = []

    for c_m, c_s in zip(df_m.columns, df_s.columns):
        b = (
            alt.Chart(tog)
            .mark_bar()
            .encode(x=alt.X(c_m, type="quantitative"), y=alt.Y(index_col, type="nominal"))
        )

        err = (
            alt.Chart(tog)
            .mark_errorbar()
            .encode(x=alt.X(c_m, type="quantitative"), xError=c_s, y=alt.Y(index_col, type="nominal"))
        )

        v = b + err
        intent = [lux.Clause(c_m, data_type="quantitative", data_model="measure"),
                  lux.Clause(index_col, data_type="nominal", data_model="dimension")]
        cv = CustomVis(intent, v, tog)
        cv.mark = "bar"
        vl.append(cv)
    return vl


def plot_df_mean_errorbar(df_m, df_s):
    """
    In:
        df_m: results of df.mean() (as a dataframe)
        df_s: result of df.std() (as a dataframe)

    Returns:
        CustomVis of this object
    """
    tog = df_m.join(df_s).reset_index()

    x_name = "mean"
    y_name = "index"

    b = (
        alt.Chart(tog)
        .mark_bar()
        .encode(x=alt.X(x_name, type="quantitative"), y=alt.Y(y_name, type="nominal"))
    )

    err = (
        alt.Chart(tog)
        .mark_errorbar()
        .encode(x=alt.X(x_name, type="quantitative"), xError="std", y=alt.Y(y_name, type="nominal"))
    )

    v = b + err

    intent = [
        lux.Clause(x_name, data_type="quantitative", data_model="measure"),
        lux.Clause(y_name, data_type="nominal", data_model="dimension"),
    ]

    cv = CustomVis(intent, v, tog)
    cv.mark = "bar"
    return cv


##########
# Utils  #
##########
def rename_cg_history(ldf):
    """
    Rename the columns of ldf based on the aggregation that produced this df
    """
    updated_col_names, f_map = get_cols_agg_name(ldf)
    ldf_renamed = ldf.rename(columns=updated_col_names)

    inverted_map = {}
    for k, v in updated_col_names.items():
        inverted_map[v] = k

    ldf_renamed._parent_df = ldf._parent_df  # omit the rename from tree

    return ldf_renamed, f_map, inverted_map


def get_cols_agg_name(ldf):
    """
    Rename columns according to their aggregation function if possible

    Returns
        dict of {old_cols : new_cols}
        dict of
    """
    valid_agg_funcs = [
        "size",
        "mean",
        "min",
        "max",
        "count",
        "sum",
        "prod",
        "median",
        "std",
        "var",
        "sem",
    ]

    all_cols = ldf.columns
    col_agg_d = {}

    start_index = -1
    n = len(ldf.history._events)

    try:
        # find most recent groupby
        i = n - 1
        while i > -1:
            e = ldf.history._events[i]
            if e.op_name == "groupby":
                start_index = i + 1
                break
            i -= 1

        # look after most recent groupby
        if start_index != -1:
            for i in range(start_index, n):
                e = ldf.history._events[i]
                if e.op_name in valid_agg_funcs:
                    process_update_item(e, col_agg_d, all_cols)
                else:
                    col_agg_d = {}  # something else in history so must reset

        # look at most recent function otherwise
        else:
            e = ldf.history._events[-1]
            if e.op_name in valid_agg_funcs:
                process_update_item(e, col_agg_d, all_cols)

    except (IndexError, AttributeError):
        pass

    finally:
        ret_d = {}
        f_map = {}
        for k, v in col_agg_d.items():
            s = k
            if k != v:
                s = f"{k} ({v})"
            ret_d[k] = s
            f_map[s] = v

        if "index" in ret_d:
            ret_d["index"] = "index"

        return ret_d, f_map


def process_update_item(evnt, d, all_cols):
    curr_op = evnt.op_name
    curr_cols = evnt.cols
    # if columns on the history item use these, otherwise use all
    update_cols = all_cols
    if len(curr_cols):
        update_cols = curr_cols
    for c in update_cols:
        d[c] = curr_op
