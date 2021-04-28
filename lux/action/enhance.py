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


def enhance(ldf):
    """
    Given a set of vis, generates possible visualizations when an additional attribute is added to the current vis.

    Parameters
    ----------
    ldf : lux.core.frame
            LuxDataFrame with underspecified intent.

    Returns
    -------
    recommendations : Dict[str,obj]
            object with a collection of visualizations that result from the Enhance action.
    """

    filters = utils.get_filter_specs(ldf._intent)
    # Collect variables that already exist in the intent
    attr_specs = list(filter(lambda x: x.value == "" and x.attribute != "Record", ldf._intent))
    fltr_str = [fltr.attribute + fltr.filter_op + str(fltr.value) for fltr in filters]
    attr_str = [str(clause.attribute) for clause in attr_specs]
    intended_attrs = f'<p class="highlight-intent">{", ".join(attr_str + fltr_str)}</p>'
    if len(attr_specs) == 1:
        recommendation = {
            "action": "Enhance",
            "description": f"Augmenting current {intended_attrs} intent with additional attribute.",
            "long_description": f"Enhance adds an additional attribute displaying how {intended_attrs} changes with respect to other attributes. Visualizations are ranked based on interestingness. The top 15 visualizations are displayed.",
        }
    elif len(attr_specs) == 2:
        recommendation = {
            "action": "Enhance",
            "description": f"Further breaking down current {intended_attrs} intent by additional attribute.",
            "long_description": f"Enhance adds an additional attribute as the color to break down the {intended_attrs} distribution",
        }
    # if there are too many column attributes, return don't generate Enhance recommendations
    else:
        recommendation = {"action": "Enhance"}
        recommendation["collection"] = []
        return recommendation
    intent = ldf._intent.copy()
    # Clear channel so that channel not enforced based on input vis intent
    for clause in intent:
        clause.channel = ""
    intent = filters + attr_specs
    intent.append("?")
    vlist = lux.vis.VisList.VisList(intent, ldf)

    # Then use the data populated in the vis list to compute score
    for vis in vlist:
        vis.score = interestingness(vis, ldf)

    vlist.sort()
    vlist = vlist.showK()
    recommendation["collection"] = vlist
    return recommendation
