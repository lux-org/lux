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

    n_dim = 0
    n_msr = 0

    filter_specs = utils.get_filter_specs(vis._inferred_intent)
    vis_attrs_specs = utils.get_attrs_specs(vis._inferred_intent)

    record_attrs = list(
        filter(
            lambda x: x.attribute == "Record" and x.data_model == "measure",
            vis_attrs_specs,
        )
    )
    n_record = len(record_attrs)
    for clause in vis_attrs_specs:
        if clause.attribute != "Record":
            if clause.data_model == "dimension":
                n_dim += 1
            if clause.data_model == "measure":
                n_msr += 1
    n_filter = len(filter_specs)
    attr_specs = [clause for clause in vis_attrs_specs if clause.attribute != "Record"]
    dimension_lst = vis.get_attr_by_data_model("dimension")
    measure_lst = vis.get_attr_by_data_model("measure")
    v_size = len(vis.data)
    # Line/Bar Chart
    # print("r:", n_record, "m:", n_msr, "d:",n_dim)
    if n_dim == 1 and (n_msr == 0 or n_msr == 1):
        if v_size < 2:
            return -1
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
            return weighted_correlation(vis.data["xBinStart"], vis.data["yBinStart"], vis.data["count"])
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

        contingency_table = []
        groupby_cardinality = ldf.cardinality[groupby_column]
        groupby_unique_vals = ldf.unique_values[groupby_column]
        for c in range(0, groupby_cardinality):
            contingency_table.append(
                vis.data[vis.data[groupby_column] == groupby_unique_vals[c]][measure_column]
            )
        score = 0.12
        # ValueError results if an entire column of the contingency table is 0, can happen if an applied filter results in
        # a category having no counts

        try:
            color_cardinality = ldf.cardinality[color_column]
            # scale down score based on number of categories
            chi2_score = chi2_contingency(contingency_table)[0] * 0.9 ** (
                color_cardinality + groupby_cardinality
            )
            score = min(0.10, chi2_score)
        except ValueError:
            pass
        return score
    # Default
    else:
        return -1


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


def deviation_from_overall(vis: Vis, ldf: LuxDataFrame, filter_specs: list, msr_attribute: str) -> int:
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

    Returns
    -------
    int
            Score describing how different the vis is from the overall vis
    """
    v_filter_size = get_filtered_size(filter_specs, ldf)
    v_size = len(vis.data)
    v_filter = vis.data[msr_attribute]
    total = v_filter.sum()
    v_filter = v_filter / total  # normalize by total to get ratio
    if total == 0:
        return 0
    # Generate an "Overall" Vis (TODO: This is computed multiple times for every vis, alternative is to directly access df.current_vis but we do not have guaruntee that will always be unfiltered vis (in the non-Filter action scenario))
    import copy

    unfiltered_vis = copy.copy(vis)
    # Remove filters, keep only attribute intent
    unfiltered_vis._inferred_intent = utils.get_attrs_specs(vis._inferred_intent)
    ldf.executor.execute([unfiltered_vis], ldf)

    v = unfiltered_vis.data[msr_attribute]
    v = v / v.sum()
    assert len(v) == len(v_filter), "Data for filtered and unfiltered vis have unequal length."
    sig = v_filter_size / v_size  # significance factor
    # Euclidean distance as L2 function

    rankSig = 1  # category measure value ranking significance factor
    # if the vis is a barchart, count how many categories' rank, based on measure value, changes after the filter is applied
    if vis.mark == "bar":
        dimList = vis.get_attr_by_data_model("dimension")

        # use Pandas rank function to calculate rank positions for each category
        v_rank = unfiltered_vis.data.rank()
        v_filter_rank = vis.data.rank()
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
    C = ldf.cardinality[dimension_lst[0].attribute]
    D = (0.9) ** C  # cardinality-based discounting factor
    v_flat = pd.Series([1 / C] * len(v))
    if is_datetime(v):
        v = v.astype("int")
    return D * euclidean(v, v_flat)


def mutual_information(v_x: list, v_y: list) -> int:
    # Interestingness metric for two measure attributes
    # Calculate maximal information coefficient (see Murphy pg 61) or Pearson's correlation
    from sklearn.metrics import mutual_info_score

    return mutual_info_score(v_x, v_y)


def monotonicity(vis: Vis, attr_specs: list, ignore_identity: bool = True) -> int:
    """
    Monotonicity measures there is a monotonic trend in the scatterplot, whether linear or not.
    This score is computed as the square of the Spearman correlation coefficient, which is the Pearson correlation on the ranks of x and y.
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
    from scipy.stats import spearmanr

    msr1 = attr_specs[0].attribute
    msr2 = attr_specs[1].attribute

    if ignore_identity and msr1 == msr2:  # remove if measures are the same
        return -1
    v_x = vis.data[msr1]
    v_y = vis.data[msr2]

    import warnings

    with warnings.catch_warnings():
        warnings.filterwarnings("error")
        try:
            score = (spearmanr(v_x, v_y)[0]) ** 2
        except (RuntimeWarning):
            # RuntimeWarning: invalid value encountered in true_divide (occurs when v_x and v_y are uniform, stdev in denominator is zero, leading to spearman's correlation as nan), ignore these cases.
            score = -1

    if pd.isnull(score):
        return -1
    else:
        return score
    # import scipy.stats
    # return abs(scipy.stats.pearsonr(v_x,v_y)[0])
