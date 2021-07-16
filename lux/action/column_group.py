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

import lux
from lux.interestingness.interestingness import interestingness
from lux.processor.Compiler import Compiler
from lux.utils import utils

from lux.vis.Vis import Vis
from lux.vis.VisList import VisList
import pandas as pd

from lux.implicit import cg_plotter

from IPython.core.debugger import set_trace


def column_group(ldf):
    recommendation = {
        "action": "Column Groups",
        "description": "Shows charts of possible visualizations with respect to the column-wise index.",
        "long_description": 'A column index can be thought of as an extra column that indicates the values that the user is interested in. \
            Lux focuses on visualizing named dataframe indices, i.e., indices with a non-null name property, as a proxy of the attribute \
                that the user is interested in or have operated on (e.g., group-by attribute). In particular, dataframes with named indices \
                    are often pre-aggregated, so Lux visualizes exactly the values that the dataframe portrays.  \
                        <a href="https://lux-api.readthedocs.io/en/latest/source/advanced/indexgroup.html" target="_blank">More details</a>',
    }

    ldf, f_map, inverted_col_map = cg_plotter.rename_cg_history(ldf)

    ldf_flat = ldf
    if isinstance(ldf.columns, pd.DatetimeIndex):
        ldf_flat.columns = ldf_flat.columns.format()

    # use a single shared ldf_flat so that metadata doesn't need to be computed for every vis
    ldf_flat = ldf_flat.reset_index()
    vlst = VisList([], ldf_flat)

    # dont compute if this is the result of describe or value counts
    if len(ldf.history) and (
        ldf.history._events[-1].op_name == "describe"
        or ldf.history._events[-1].op_name == "value_counts"
    ):
        recommendation["collection"] = vlst
        return recommendation

    if ldf.index.nlevels == 1:
        if ldf.index.name:
            index_column_name = ldf.index.name
        else:
            index_column_name = "index"
        if isinstance(ldf.columns, pd.DatetimeIndex):
            ldf.columns = ldf.columns.to_native_types()

        # df.mean() case
        if len(ldf.columns) == 1 and ldf.columns[0] == "mean":
            try:
                std_ser = ldf._parent_df.std()  # is a series
                df_s = pd.DataFrame(std_ser).rename(columns={0: "std"})
                v = cg_plotter.plot_df_mean_errorbar(ldf, df_s)
                vlst._collection.extend([v])

            except AttributeError:  # tree is corrupted
                v = cg_plotter.plot_col_vis(index_column_name, "mean")
                vlst = VisList([v], ldf_flat)

        # df.groupby.mean() case
        elif isinstance(ldf._parent_df, lux.core.groupby.LuxGroupBy) and all(
            [j == "mean" for j in f_map.values()]
        ):
            try:
                df_s = ldf._parent_df.std()
                df_s = df_s.rename(columns={c: f"{c} (std)" for c in df_s.columns})
                vl = cg_plotter.plot_gb_mean_errorbar(ldf, df_s)
                vlst._collection.extend(vl)

            except AttributeError:  # tree is corrupted
                collection = []
                for a in ldf.columns:
                    vis = cg_plotter.plot_col_vis(index_column_name, a)
                    collection.append(vis)
                vlst = VisList(collection, ldf_flat)

        else:
            collection = []
            mean_collection = []
            for attribute in ldf.columns:
                if ldf[attribute].dtype != "object" and (attribute != "index"):
                    if (
                        (attribute in f_map)
                        and (f_map[attribute] == "mean")
                        and isinstance(ldf._parent_df, lux.core.groupby.LuxGroupBy)
                    ):

                        try:
                            _this_c_df = ldf[[attribute]]  # select col as df
                            old_col_name = inverted_col_map[attribute]
                            df_s = pd.DataFrame(ldf._parent_df[old_col_name].std())  # as df
                            df_s = df_s.rename(columns={c: f"{c} (std)" for c in df_s.columns})

                            vl = cg_plotter.plot_gb_mean_errorbar(_this_c_df, df_s)
                            mean_collection.extend(vl)

                        except ValueError:
                            vis = cg_plotter.plot_col_vis(index_column_name, attribute)
                            collection.append(vis)

                    else:
                        vis = cg_plotter.plot_col_vis(index_column_name, attribute)
                        collection.append(vis)
                elif ldf[attribute].dtype == "object" and (attribute != "index"):
                    if (
                        (attribute in f_map)
                        and (f_map[attribute] == "std")
                        and all(
                            ldf[attribute].map(
                                lambda x: isinstance(x, pd._libs.tslibs.timedeltas.Timedelta)
                                or pd.api.types.is_float_dtype(x)
                            )
                        )
                    ):
                        timedelta_index = ldf_flat[attribute].map(
                            lambda x: isinstance(x, pd._libs.tslibs.timedeltas.Timedelta)
                        )
                        ldf_flat[attribute][timedelta_index] = ldf_flat[attribute][
                            timedelta_index
                        ] / pd.to_timedelta(1, unit="D")
                        ldf_flat[attribute] = ldf_flat[attribute].astype("float64")
                        vis = cg_plotter.plot_std_bar(ldf_flat, attribute)
                        mean_collection.append(vis)
            vlst = VisList(collection, ldf_flat)
            vlst._collection.extend(mean_collection)
    # Note that we are not computing interestingness score here because we want to preserve the arrangement of the aggregated ldf

    recommendation["collection"] = vlst
    return recommendation
