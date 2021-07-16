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
from lux.vis.VisList import VisList
from lux.vis.Vis import Vis


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
    implicit_col_list = ldf.history.get_implicit_intent(ldf.columns)

    intent = []
    intended_attrs = "columns"

    # Normal enhance
    if ldf._intent:
        filters = utils.get_filter_specs(ldf._intent)
        attr_specs = list(filter(lambda x: x.value == "" and x.attribute != "Record", ldf._intent))
        fltr_str = [fltr.attribute + fltr.filter_op + str(fltr.value) for fltr in filters]
        attr_str = [str(clause.attribute) for clause in attr_specs]

        intended_attrs = f'<p class="highlight-intent">{", ".join(attr_str + fltr_str)}</p>'
        intent = ldf._intent.copy()
        # Clear channel so that channel not enforced based on input vis intent
        for clause in intent:
            clause.channel = ""
        intent = filters + attr_specs
        intent.append("?")

    # implicit enhance
    elif implicit_col_list:
        intended_attrs = f'<p class="highlight-intent">{implicit_col_list[0]}</p>'
        intent = [implicit_col_list[0], "?"]

    vlist = VisList(intent, ldf)

    for vis in vlist:
        vis.score = interestingness(vis, ldf)

    vlist.sort(intent_cols=implicit_col_list)
    vlist = vlist.showK()

    recommendation = {
        "action": "Enhance",
        "collection": vlist,
        "description": f"Augmenting {intended_attrs} with an additional attribute.",
        "long_description": f"""Enhance adds an additional attribute displaying how 
        {intended_attrs} changes with respect to other attributes. 
        Visualizations are ranked based on interestingness and implicit interest.""",
    }

    return recommendation
