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


def row_group(ldf):
    recommendation = {
        "action": "Row Groups",
        "description": "Shows charts of possible visualizations with respect to the row-wise index.",
        "long_description": 'A row index can be thought of as an extra row that indicates the values that the user is interested in. \
            Lux focuses on visualizing named dataframe indices, i.e., indices with a non-null name property, as a proxy of the attribute \
                that the user is interested in or have operated on (e.g., group-by attribute). In particular, dataframes with named indices \
                    are often pre-aggregated, so Lux visualizes exactly the values that the dataframe portrays. \
                        <a href="https://lux-api.readthedocs.io/en/latest/source/advanced/indexgroup.html" target="_blank">More details</a>',
    }
    collection = []

    if ldf.index.nlevels == 1:
        if ldf.columns.name is not None:
            dim_name = ldf.columns.name
        else:
            dim_name = "index"
        for row_id in range(len(ldf)):
            row = ldf.iloc[
                row_id,
            ]
            rowdf = row.reset_index()
            # if (dim_name =="index"): #TODO: need to change this to auto-detect
            # 	rowdf.data_type_lookup["index"]="nominal"
            # 	rowdf.data_model_lookup["index"]="dimension"
            # 	rowdf.cardinality["index"]=len(rowdf)
            # if isinstance(ldf.columns,pd.DatetimeIndex):
            # 	rowdf.data_type_lookup[dim_name]="temporal"
            vis = Vis(
                [
                    dim_name,
                    lux.Clause(row.name, data_model="measure", aggregation=None),
                ],
                rowdf,
            )
            collection.append(vis)
    vlst = VisList(collection)
    # Note that we are not computing interestingness score here because we want to preserve the arrangement of the aggregated data

    recommendation["collection"] = vlst
    return recommendation
