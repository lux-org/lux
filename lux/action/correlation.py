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
from lux.core.frame import LuxDataFrame
from lux.vis.VisList import VisList
from lux.utils import utils


# change ignore_transpose to false for now.
def correlation(ldf: LuxDataFrame, ignore_transpose: bool = True):
    """
    Generates bivariate visualizations that represent all pairwise relationships in the data.

    Parameters
    ----------
    ldf : LuxDataFrame
            LuxDataFrame with underspecified intent.

    ignore_transpose: bool
            Boolean flag to ignore pairs of attributes whose transpose are already computed (i.e., {X,Y} will be ignored if {Y,X} is already computed)

    Returns
    -------
    recommendations : Dict[str,obj]
            object with a collection of visualizations that result from the Correlation action.
    """

    import numpy as np

    filter_specs = utils.get_filter_specs(ldf._intent)
    intent = [
        lux.Clause("?", data_model="measure"),
        lux.Clause("?", data_model="measure"),
    ]
    intent.extend(filter_specs)
    vlist = VisList(intent, ldf)
    examples = ""
    if len(vlist) > 1:
        measures = vlist[0].get_attr_by_data_model("measure")
        if len(measures) >= 2:
            examples = f" (e.g., {measures[0].attribute}, {measures[1].attribute})"
    recommendation = {
        "action": "Correlation",
        "description": "Show relationships between two <p class='highlight-descriptor'>quantitative</p> attributes.",
        "long_description": f"Correlation searches through all pairwise relationship between two quantitative attributes\
            {examples}. The visualizations are ranked from most to least linearly correlated based on \
                their Pearson’s correlation score.",
    }
    ignore_rec_flag = False
    # Doesn't make sense to compute correlation if less than 4 data values
    if len(ldf) < 5:
        ignore_rec_flag = True
    # Then use the data populated in the vis list to compute score
    for vis in vlist:
        measures = vis.get_attr_by_data_model("measure")
        if len(measures) < 2:
            raise ValueError(
                f"Can not compute correlation between {[x.attribute for x in ldf.columns]} since less than 2 measure values present."
            )
        msr1 = measures[0].attribute
        msr2 = measures[1].attribute
        if ignore_transpose:
            check_transpose = check_transpose_not_computed(vlist, msr1, msr2)
        else:
            check_transpose = True
        if check_transpose:
            vis.score = interestingness(vis, ldf)
        else:
            vis.score = -1
    if ignore_rec_flag:
        recommendation["collection"] = []
        return recommendation
    vlist.sort()
    vlist = vlist.showK()
    recommendation["collection"] = vlist
    return recommendation


def check_transpose_not_computed(vlist: VisList, a: str, b: str):
    transpose_exist = list(
        filter(
            lambda x: (x._inferred_intent[0].attribute == b) and (x._inferred_intent[1].attribute == a),
            vlist,
        )
    )
    if len(transpose_exist) > 0:
        return transpose_exist[0].score == -1
    else:
        return False
