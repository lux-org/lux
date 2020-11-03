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

import pandas
from lux.vis.VisList import VisList
from lux.vis.Vis import Vis
from lux.core.frame import LuxDataFrame
from lux.executor.Executor import Executor
from lux.utils import utils
import math


class SQLExecutor(Executor):
    """
    Given a Vis objects with complete specifications, fetch and process data using SQL operations.
    """

    def __init__(self):
        self.name = "Executor"
        self.selection = []
        self.tables = []
        self.filters = ""

    def __repr__(self):
        return f"<Executor>"

    @staticmethod
    def execute(vislist: VisList, ldf: LuxDataFrame):
        import pandas as pd

        """
        Given a VisList, fetch the data required to render the vis
        1) Apply filters
        2) Retreive relevant attribute
        3) return a DataFrame with relevant results
        """
        for vis in vislist:
            # Select relevant data based on attribute information
            attributes = set([])
            for clause in vis._inferred_intent:
                if clause.attribute:
                    if clause.attribute == "Record":
                        attributes.add(clause.attribute)
                    # else:
                    attributes.add(clause.attribute)
            if vis.mark not in ["bar", "line", "histogram"]:
                where_clause, filterVars = SQLExecutor.execute_filter(vis)
                required_variables = attributes | set(filterVars)
                required_variables = ",".join(required_variables)
                row_count = list(
                    pd.read_sql(
                        "SELECT COUNT(*) FROM {} {}".format(
                            ldf.table_name, where_clause
                        ),
                        ldf.SQLconnection,
                    )["count"]
                )[0]
                if row_count > 10000:
                    query = "SELECT {} FROM {} {} ORDER BY random() LIMIT 10000".format(
                        required_variables, ldf.table_name, where_clause
                    )
                else:
                    query = "SELECT {} FROM {} {}".format(
                        required_variables, ldf.table_name, where_clause
                    )
                data = pd.read_sql(query, ldf.SQLconnection)
                vis._vis_data = utils.pandas_to_lux(data)
            if vis.mark == "bar" or vis.mark == "line":
                SQLExecutor.execute_aggregate(vis, ldf)
            elif vis.mark == "histogram":
                SQLExecutor.execute_binning(vis, ldf)

    @staticmethod
    def execute_aggregate(vis: Vis, ldf: LuxDataFrame):
        import pandas as pd

        x_attr = vis.get_attr_by_channel("x")[0]
        y_attr = vis.get_attr_by_channel("y")[0]
        groupby_attr = ""
        measure_attr = ""
        if y_attr.aggregation != "":
            groupby_attr = x_attr
            measure_attr = y_attr
            agg_func = y_attr.aggregation
        if x_attr.aggregation != "":
            groupby_attr = y_attr
            measure_attr = x_attr
            agg_func = x_attr.aggregation

        if measure_attr != "":
            # barchart case, need count data for each group
            if measure_attr.attribute == "Record":
                where_clause, filterVars = SQLExecutor.execute_filter(vis)
                count_query = "SELECT {}, COUNT({}) FROM {} {} GROUP BY {}".format(
                    groupby_attr.attribute,
                    groupby_attr.attribute,
                    ldf.table_name,
                    where_clause,
                    groupby_attr.attribute,
                )
                vis._vis_data = pd.read_sql(count_query, ldf.SQLconnection)
                vis._vis_data = vis.data.rename(columns={"count": "Record"})
                vis._vis_data = utils.pandas_to_lux(vis.data)

            else:
                where_clause, filterVars = SQLExecutor.execute_filter(vis)
                if agg_func == "mean":
                    mean_query = (
                        "SELECT {}, AVG({}) as {} FROM {} {} GROUP BY {}".format(
                            groupby_attr.attribute,
                            measure_attr.attribute,
                            measure_attr.attribute,
                            ldf.table_name,
                            where_clause,
                            groupby_attr.attribute,
                        )
                    )
                    vis._vis_data = pd.read_sql(mean_query, ldf.SQLconnection)
                    vis._vis_data = utils.pandas_to_lux(vis.data)
                if agg_func == "sum":
                    mean_query = (
                        "SELECT {}, SUM({}) as {} FROM {} {} GROUP BY {}".format(
                            groupby_attr.attribute,
                            measure_attr.attribute,
                            measure_attr.attribute,
                            ldf.table_name,
                            where_clause,
                            groupby_attr.attribute,
                        )
                    )
                    vis._vis_data = pd.read_sql(mean_query, ldf.SQLconnection)
                    vis._vis_data = utils.pandas_to_lux(vis.data)
                if agg_func == "max":
                    mean_query = (
                        "SELECT {}, MAX({}) as {} FROM {} {} GROUP BY {}".format(
                            groupby_attr.attribute,
                            measure_attr.attribute,
                            measure_attr.attribute,
                            ldf.table_name,
                            where_clause,
                            groupby_attr.attribute,
                        )
                    )
                    vis._vis_data = pd.read_sql(mean_query, ldf.SQLconnection)
                    vis._vis_data = utils.pandas_to_lux(vis.data)

            # pad empty categories with 0 counts after filter is applied
            all_attr_vals = ldf.unique_values[groupby_attr.attribute]
            result_vals = list(vis.data[groupby_attr.attribute])
            if len(result_vals) != len(all_attr_vals):
                # For filtered aggregation that have missing groupby-attribute values, set these aggregated value as 0, since no datapoints
                for vals in all_attr_vals:
                    if vals not in result_vals:
                        vis.data.loc[len(vis.data)] = [vals] + [0] * (
                            len(vis.data.columns) - 1
                        )

    @staticmethod
    def execute_binning(vis: Vis, ldf: LuxDataFrame):
        import numpy as np
        import pandas as pd

        bin_attribute = list(filter(lambda x: x.bin_size != 0, vis._inferred_intent))[0]
        if not math.isnan(vis.data.min_max[bin_attribute.attribute][0]) and math.isnan(
            vis.data.min_max[bin_attribute.attribute][1]
        ):
            num_bins = bin_attribute.bin_size
            attr_min = min(ldf.unique_values[bin_attribute.attribute])
            attr_max = max(ldf.unique_values[bin_attribute.attribute])
            attr_type = type(ldf.unique_values[bin_attribute.attribute][0])

            # need to calculate the bin edges before querying for the relevant data
            bin_width = (attr_max - attr_min) / num_bins
            upper_edges = []
            for e in range(1, num_bins):
                curr_edge = attr_min + e * bin_width
                if attr_type == int:
                    upper_edges.append(str(math.ceil(curr_edge)))
                else:
                    upper_edges.append(str(curr_edge))
            upper_edges = ",".join(upper_edges)
            vis_filter, filter_vars = SQLExecutor.execute_filter(vis)
            bin_count_query = "SELECT width_bucket, COUNT(width_bucket) FROM (SELECT width_bucket({}, '{}') FROM {}) as Buckets GROUP BY width_bucket ORDER BY width_bucket".format(
                bin_attribute.attribute, "{" + upper_edges + "}", ldf.table_name
            )
            bin_count_data = pd.read_sql(bin_count_query, ldf.SQLconnection)

            # counts,binEdges = np.histogram(ldf[bin_attribute.attribute],bins=bin_attribute.bin_size)
            # binEdges of size N+1, so need to compute binCenter as the bin location
            upper_edges = [float(i) for i in upper_edges.split(",")]
            if attr_type == int:
                bin_centers = np.array(
                    [math.ceil((attr_min + attr_min + bin_width) / 2)]
                )
            else:
                bin_centers = np.array([(attr_min + attr_min + bin_width) / 2])
            bin_centers = np.append(
                bin_centers,
                np.mean(np.vstack([upper_edges[0:-1], upper_edges[1:]]), axis=0),
            )
            if attr_type == int:
                bin_centers = np.append(
                    bin_centers,
                    math.ceil((upper_edges[len(upper_edges) - 1] + attr_max) / 2),
                )
            else:
                bin_centers = np.append(
                    bin_centers, (upper_edges[len(upper_edges) - 1] + attr_max) / 2
                )

            if len(bin_centers) > len(bin_count_data):
                bucket_lables = bin_count_data["width_bucket"].unique()
                for i in range(0, len(bin_centers)):
                    if i not in bucket_lables:
                        bin_count_data = bin_count_data.append(
                            pd.DataFrame([[i, 0]], columns=bin_count_data.columns)
                        )
            vis._vis_data = pd.DataFrame(
                np.array([bin_centers, list(bin_count_data["count"])]).T,
                columns=[bin_attribute.attribute, "Number of Records"],
            )
            vis._vis_data = utils.pandas_to_lux(vis.data)

    @staticmethod
    # takes in a vis and returns an appropriate SQL WHERE clause that based on the filters specified in the vis's _inferred_intent
    def execute_filter(vis: Vis):
        where_clause = []
        filters = utils.get_filter_specs(vis._inferred_intent)
        filter_vars = []
        if filters:
            for f in range(0, len(filters)):
                if f == 0:
                    where_clause.append("WHERE")
                else:
                    where_clause.append("AND")
                where_clause.extend(
                    [
                        str(filters[f].attribute),
                        str(filters[f].filter_op),
                        "'" + str(filters[f].value) + "'",
                    ]
                )
                if filters[f].attribute not in filter_vars:
                    filter_vars.append(filters[f].attribute)
        if where_clause == []:
            return ("", [])
        else:
            where_clause = " ".join(where_clause)
        return (where_clause, filter_vars)
