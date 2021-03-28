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
    collection = []
    
    set_trace()
    
    # update column names to include aggregation 
    updated_col_names, f_map = get_cols_agg_name(ldf)
    ldf = ldf.rename(columns = updated_col_names)

    ldf_flat = ldf
    if isinstance(ldf.columns, pd.DatetimeIndex):
        ldf_flat.columns = ldf_flat.columns.format()

    # use a single shared ldf_flat so that metadata doesn't need to be computed for every vis
    ldf_flat = ldf_flat.reset_index()
    if ldf.index.nlevels == 1:
        if ldf.index.name:
            index_column_name = ldf.index.name
        else:
            index_column_name = "index"
        if isinstance(ldf.columns, pd.DatetimeIndex):
            ldf.columns = ldf.columns.to_native_types()
        
        for attribute in ldf.columns:
            if ldf[attribute].dtype != "object" and (attribute != "index"):

                if f_map[attribute] == "mean": 
                    # TODO 
                    # get std 
                    # produce vis with std


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
                else:
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
                collection.append(vis)
    vlst = VisList(collection, ldf_flat)
    # Note that we are not computing interestingness score here because we want to preserve the arrangement of the aggregated ldf

    recommendation["collection"] = vlst
    return recommendation


def get_cols_agg_name(ldf):
    """
    Rename columns according to their aggregation function if possible 

    Returns 
        dict of {old_cols : new_cols}
        dict of 
    """
    valid_agg_funcs = ["size", "mean", "min", "max", "count", "sum", "prod", "median", "std", "var", "sem"]

    all_cols = ldf.columns 
    col_agg_d = {}
    
    for e in ldf.history._events:
        if e.op_name in valid_agg_funcs: # should check if follows "groupby"?
            curr_op = e.op_name
            curr_cols = e.cols
            
            update_cols = all_cols
            
            if len(curr_cols) != 0:
                update_cols = curr_cols
                
            for c in update_cols:
                col_agg_d[c] = curr_op
    
    ret_d = {}
    f_map = {}
    for k, v in col_agg_d.items():
        s = k
        if k!=v:
            s = f"{k} ({v})"
        ret_d[k] = s
        f_map[s] = v

    if "index" in ret_d:
        ret_d["index"] = "index"
    
    return ret_d, f_map
