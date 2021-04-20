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

from lux.core.frame import LuxDataFrame
from lux.vis.Vis import Vis
from lux.executor.PandasExecutor import PandasExecutor
from lux.utils import utils

import pandas as pd
import numpy as np
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from scipy.spatial.distance import euclidean
import lux
from lux.utils.utils import get_filter_specs
from lux.interestingness.similarity import preprocess, euclidean_dist
from lux.vis.VisList import VisList
import warnings


def interestingness(vis: Vis, ldf: LuxDataFrame) -> int:
    """
    Compute the interestingness score of the vis.
    The interestingness metric is dependent on the vis type.

    Parameters
    ----------
    vis : Vis
    ldf : LuxDataFrame

    Returns
    -------
    int
            Interestingness Score
    """
    if vis.data is None or len(vis.data) == 0:
        return -1
        # raise Exception("Vis.data needs to be populated before interestingness can be computed. Run Executor.execute(vis,ldf).")
    try:
        filter_specs = utils.get_filter_specs(vis._inferred_intent)
        vis_attrs_specs = utils.get_attrs_specs(vis._inferred_intent)
        n_dim = vis._ndim
        n_msr = vis._nmsr
        n_filter = len(filter_specs)
        attr_specs = [clause for clause in vis_attrs_specs if clause.attribute != "Record"]
        dimension_lst = vis.get_attr_by_data_model("dimension")
        measure_lst = vis.get_attr_by_data_model("measure")
        v_size = len(vis.data)

        if (
            n_dim == 1
            and (n_msr == 0 or n_msr == 1)
            and ldf.current_vis is not None
            and vis.get_attr_by_channel("y")[0].data_type == "quantitative"
            and len(ldf.current_vis) == 1
            and ldf.current_vis[0].mark == "line"
            and len(get_filter_specs(ldf.intent)) > 0
        ):
            query_vc = VisList(ldf.current_vis, ldf)
            query_vis = query_vc[0]
            preprocess(query_vis)
            preprocess(vis)
            return 1 - euclidean_dist(query_vis, vis)

        # Line/Bar Chart
        if n_dim == 1 and (n_msr == 0 or n_msr == 1):
            if v_size < 2:
                return -1

            if vis.mark == "geographical":
                return n_distinct(vis, dimension_lst, measure_lst)
            if n_filter == 0:
                return unevenness(vis, ldf, measure_lst, dimension_lst)
            elif n_filter == 1:
                return deviation_from_overall(vis, ldf, filter_specs, measure_lst[0].attribute)
        # Histogram
        elif n_dim == 0 and n_msr == 1:
            if v_size < 2:
                return -1
            if n_filter == 0 and "Number of Records" in vis.data:
                if "Number of Records" in vis.data:
                    v = vis.data["Number of Records"]
                    return skewness(v)
            elif n_filter == 1 and "Number of Records" in vis.data:
                return deviation_from_overall(vis, ldf, filter_specs, "Number of Records")
            return -1
        # Scatter Plot
        elif n_dim == 0 and n_msr == 2:
            if v_size < 10:
                return -1
            if vis.mark == "heatmap":
                return weighted_correlation(
                    vis.data["xBinStart"], vis.data["yBinStart"], vis.data["count"]
                )
            if n_filter == 1:
                v_filter_size = get_filtered_size(filter_specs, vis.data)
                sig = v_filter_size / v_size
            else:
                sig = 1
            return sig * monotonicity(vis, attr_specs)
        # Scatterplot colored by Dimension
        elif n_dim == 1 and n_msr == 2:
            if v_size < 10:
                return -1
            color_attr = vis.get_attr_by_channel("color")[0].attribute

            C = ldf.cardinality[color_attr]
            if C < 40:
                return 1 / C
            else:
                return -1
        # Scatterplot colored by dimension
        elif n_dim == 1 and n_msr == 2:
            return 0.2
        # Scatterplot colored by measure
        elif n_msr == 3:
            return 0.1
        # colored line and barchart cases
        elif vis.mark == "line" and n_dim == 2:
            return 0.15
        # for colored bar chart, scoring based on Chi-square test for independence score.
        # gives higher scores to colored bar charts with fewer total categories as these charts are easier to read and thus more useful for users
        elif vis.mark == "bar" and n_dim == 2:
            from scipy.stats import chi2_contingency

            measure_column = vis.get_attr_by_data_model("measure")[0].attribute
            dimension_columns = vis.get_attr_by_data_model("dimension")

            groupby_column = dimension_columns[0].attribute
            color_column = dimension_columns[1].attribute

            contingency_tbl = pd.crosstab(
                vis.data[groupby_column],
                vis.data[color_column],
                values=vis.data[measure_column],
                aggfunc=sum,
            )

            try:
                color_cardinality = ldf.cardinality[color_column]
                groupby_cardinality = ldf.cardinality[groupby_column]
                # scale down score based on number of categories
                chi2_score = chi2_contingency(contingency_tbl)[0] * 0.9 ** (
                    color_cardinality + groupby_cardinality
                )
                score = min(0.01, chi2_score)
            except (ValueError, KeyError):
                # ValueError results if an entire column of the contingency table is 0, can happen if an applied filter results in a category having no counts
                score = -1
            return score
        # Default
        else:
            return -1
    except:
        if lux.config.interestingness_fallback:
            # Supress interestingness related issues
            warnings.warn(f"An error occurred when computing interestingness for: {vis}")
            return -1
        else:
            raise


def get_filtered_size(filter_specs, ldf):
    filter_intents = filter_specs[0]
    result = PandasExecutor.apply_filter(
        ldf, filter_intents.attribute, filter_intents.filter_op, filter_intents.value
    )
    return len(result)


def skewness(v):
    from scipy.stats import skew

    return skew(v)


def weighted_avg(x, w):
    return np.average(x, weights=w)


def weighted_cov(x, y, w):
    return np.sum(w * (x - weighted_avg(x, w)) * (y - weighted_avg(y, w))) / np.sum(w)


def weighted_correlation(x, y, w):
    # Based on https://en.wikipedia.org/wiki/Pearson_correlation_coefficient#Weighted_correlation_coefficient
    return weighted_cov(x, y, w) / np.sqrt(weighted_cov(x, x, w) * weighted_cov(y, y, w))


def deviation_from_overall(
    vis: Vis,
    ldf: LuxDataFrame,
    filter_specs: list,
    msr_attribute: str,
    exclude_nan: bool = True,
) -> int:
    """
    Difference in bar chart/histogram shape from overall chart
    Note: this function assumes that the filtered vis.data is operating on the same range as the unfiltered vis.data.

    Parameters
    ----------
    vis : Vis
    ldf : LuxDataFrame
    filter_specs : list
            List of filters from the Vis
    msr_attribute : str
            The attribute name of the measure value of the chart
    exclude_nan: bool
            Whether to include/exclude NaN values as part of the deviation calculation

    Returns
    -------
    int
            Score describing how different the vis is from the overall vis
    """
    if lux.config.executor.name == "PandasExecutor":
        if exclude_nan:
            vdata = vis.data.dropna()
        else:
            vdata = vis.data
        v_filter_size = get_filtered_size(filter_specs, ldf)
        v_size = len(vis.data)
    elif lux.config.executor.name == "SQLExecutor":
        from lux.executor.SQLExecutor import SQLExecutor

        v_filter_size = SQLExecutor.get_filtered_size(filter_specs, ldf)
        v_size = len(ldf)
        vdata = vis.data
    v_filter = vdata[msr_attribute]
    total = v_filter.sum()
    v_filter = v_filter / total  # normalize by total to get ratio
    if total == 0:
        return 0
    # Generate an "Overall" Vis (TODO: This is computed multiple times for every vis, alternative is to directly access df.current_vis but we do not have guaruntee that will always be unfiltered vis (in the non-Filter action scenario))
    import copy

    unfiltered_vis = copy.copy(vis)
    # Remove filters, keep only attribute intent
    unfiltered_vis._inferred_intent = utils.get_attrs_specs(vis._inferred_intent)
    lux.config.executor.execute([unfiltered_vis], ldf)
    if exclude_nan:
        uv = unfiltered_vis.data.dropna()
    else:
        uv = unfiltered_vis.data
    v = uv[msr_attribute]
    v = v / v.sum()
    assert len(v) == len(v_filter), "Data for filtered and unfiltered vis have unequal length."
    sig = v_filter_size / v_size  # significance factor
    # Euclidean distance as L2 function

    rankSig = 1  # category measure value ranking significance factor
    # if the vis is a barchart, count how many categories' rank, based on measure value, changes after the filter is applied
    if vis.mark == "bar":
        dimList = vis.get_attr_by_data_model("dimension")

        # use Pandas rank function to calculate rank positions for each category
        v_rank = uv.rank()
        v_filter_rank = vdata.rank()
        # go through and count the number of ranking changes between the filtered and unfiltered data
        numCategories = ldf.cardinality[dimList[0].attribute]
        for r in range(0, numCategories - 1):
            if v_rank[msr_attribute][r] != v_filter_rank[msr_attribute][r]:
                rankSig += 1
        # normalize ranking significance factor
        rankSig = rankSig / numCategories

    from scipy.spatial.distance import euclidean

    return sig * rankSig * euclidean(v, v_filter)


def unevenness(vis: Vis, ldf: LuxDataFrame, measure_lst: list, dimension_lst: list) -> int:
    """
    Measure the unevenness of a bar chart vis.
    If a bar chart is highly uneven across the possible values, then it may be interesting. (e.g., USA produces lots of cars compared to Japan and Europe)
    Likewise, if a bar chart shows that the measure is the same for any possible values the dimension attribute could take on, then it may not very informative.
    (e.g., The cars produced across all Origins (Europe, Japan, and USA) has approximately the same average Acceleration.)

    Parameters
    ----------
    vis : Vis
    ldf : LuxDataFrame
    measure_lst : list
            List of measures
    dimension_lst : list
            List of dimensions
    Returns
    -------
    int
            Score describing how uneven the bar chart is.
    """
    v = vis.data[measure_lst[0].attribute]
    v = v / v.sum()  # normalize by total to get ratio
    v = v.fillna(0)  # Some bar values may be NaN
    attr = dimension_lst[0].attribute
    if isinstance(attr, pd._libs.tslibs.timestamps.Timestamp):
        # If timestamp, use the _repr_ (e.g., TimeStamp('2020-04-05 00.000')--> '2020-04-05')
        attr = str(attr._date_repr)
    C = ldf.cardinality[attr]
    D = (0.9) ** C  # cardinality-based discounting factor
    v_flat = pd.Series([1 / C] * len(v))
    if is_datetime(v):
        v = v.astype("int")
    try:
        return D * euclidean(v, v_flat)
    except (ValueError):
        return 0.01


def mutual_information(v_x: list, v_y: list) -> int:
    # Interestingness metric for two measure attributes
    # Calculate maximal information coefficient (see Murphy pg 61) or Pearson's correlation
    from sklearn.metrics import mutual_info_score

    return mutual_info_score(v_x, v_y)


def monotonicity(vis: Vis, attr_specs: list, ignore_identity: bool = True) -> int:
    """
    Monotonicity measures there is a monotonic trend in the scatterplot, whether linear or not.
    This score is computed as the Pearson's correlation on the ranks of x and y.
    See "Graph-Theoretic Scagnostics", Wilkinson et al 2005: https://research.tableau.com/sites/default/files/Wilkinson_Infovis-05.pdf
    Parameters
    ----------
    vis : Vis
    attr_spec: list
            List of attribute Clause objects

    ignore_identity: bool
            Boolean flag to ignore items with the same x and y attribute (score as -1)

    Returns
    -------
    int
            Score describing the strength of monotonic relationship in vis
    """
    from scipy.stats import pearsonr

    msr1 = attr_specs[0].attribute
    msr2 = attr_specs[1].attribute

    if ignore_identity and msr1 == msr2:  # remove if measures are the same
        return -1
    vxy = vis.data.dropna()
    v_x = vxy[msr1]
    v_y = vxy[msr2]

    import warnings

    with warnings.catch_warnings():
        warnings.filterwarnings("error")
        try:
            score = np.abs(pearsonr(v_x, v_y)[0])
        except:
            # RuntimeWarning: invalid value encountered in true_divide (occurs when v_x and v_y are uniform, stdev in denominator is zero, leading to spearman's correlation as nan), ignore these cases.
            score = -1

    if pd.isnull(score):
        return -1
    else:
        return score


def n_distinct(vis: Vis, dimension_lst: list, measure_lst: list) -> int:
    """
    Computes how many unique values there are for a dimensional data type.
    Ignores attributes that are latitude or longitude coordinates.

    For example, if a dataset displayed earthquake magnitudes across 48 states and
    3 countries, return 48 and 3 respectively.

    Parameters
    ----------
    vis : Vis
    dimension_lst: list
            List of dimension Clause objects.
    measure_lst: list
            List of measure Clause objects.

    Returns
    -------
    int
            Score describing the number of unique values in the dimension.
    """
    if measure_lst[0].get_attr() in {"longitude", "latitude"}:
        return -1
    return vis.data[dimension_lst[0].get_attr()].nunique()
