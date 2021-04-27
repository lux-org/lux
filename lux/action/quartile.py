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

def quartile(ldf: LuxDataFrame, ignore_transpose: bool = True):
    filter_specs = utils.get_filter_specs(ldf._intent)
    intent = [
        lux.Clause("?", data_model="dimension"),
        lux.Clause("?", data_model="measure"),
    ]

    intent.extend(filter_specs)
    vlist = VisList(intent, ldf)
    examples = ""

    if len(vlist) > 1:
        measure = vlist[0].get_attr_by_data_model("measure")
        dim = vlist[0].get_attr_by_data_model("dimension")
        examples = f" (e.g., {measure[0].attribute}, {dim[0].attribute})"
        recommendation = {
        "action": "Quartile",
        "description": "Show relationships between a <p class='highlight-descriptor'>ordinal</p> attribute and a <p class='highlight-descriptor'>quantitative</p> attribute.",
        "long_description": f"Quartile searches through all pairwise relationship between ordinal and quantitative data such as \
            {examples}.",
    }
    vlist.sort()
    vlist = vlist.showK()
    recommendation["collection"] = vlist

    return recommendation

