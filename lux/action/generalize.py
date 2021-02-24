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
from lux.vis.Vis import Vis
from lux.processor.Compiler import Compiler
from lux.utils import utils
from lux.interestingness.interestingness import interestingness


def generalize(ldf):
    """
    Generates all possible visualizations when one attribute or filter from the current vis is removed.

    Parameters
    ----------
    ldf : lux.core.frame
            LuxDataFrame with underspecified intent.

    Returns
    -------
    recommendations : Dict[str,obj]
            object with a collection of visualizations that result from the Generalize action.
    """
    # takes in a dataObject and generates a list of new dataObjects, each with a single measure from the original object removed
    # -->  return list of dataObjects with corresponding interestingness scores

    output = []
    excluded_columns = []
    attributes = list(filter(lambda x: x.value == "" and x.attribute != "Record", ldf._intent))
    filters = utils.get_filter_specs(ldf._intent)

    fltr_str = [fltr.attribute + fltr.filter_op + str(fltr.value) for fltr in filters]
    attr_str = [str(clause.attribute) for clause in attributes]
    intended_attrs = f'<p class="highlight-intent">{", ".join(attr_str + fltr_str)}</p>'

    recommendation = {
        "action": "Generalize",
        "description": f"Remove an attribute or filter from {intended_attrs}.",
        "long_description": f"Remove one aspect of the Current Vis. We can either remove an attribute or filter from {intended_attrs}.",
    }
    # to observe a more general trend
    # if we do no have enough column attributes or too many, return no vis.
    if len(attributes) < 1 or len(attributes) > 4:
        recommendation["collection"] = []
        return recommendation
    # for each column specification, create a copy of the ldf's vis and remove the column specification
    # then append the vis to the output
    if len(attributes) > 1:
        for clause in attributes:
            columns = clause.attribute
            if type(columns) == list:
                for column in columns:
                    if column not in excluded_columns:
                        temp_vis = Vis(ldf.copy_intent(), score=1)
                        temp_vis.remove_column_from_spec(column, remove_first=True)
                        excluded_columns.append(column)
                        output.append(temp_vis)
            else:
                if columns not in excluded_columns:
                    temp_vis = Vis(ldf.copy_intent(), score=1)
                    temp_vis.remove_column_from_spec(columns, remove_first=True)
                    excluded_columns.append(columns)
            output.append(temp_vis)
    # for each filter specification, create a copy of the ldf's current vis and remove the filter specification,
    # then append the vis to the output
    for clause in filters:
        # new_spec = ldf._intent.copy()
        # new_spec.remove_column_from_spec(new_spec.attribute)
        temp_vis = Vis(
            ldf.current_vis[0]._inferred_intent.copy(),
            source=ldf,
            title="Overall",
            score=0,
        )
        temp_vis.remove_filter_from_spec(clause.value)
        output.append(temp_vis)

    vlist = lux.vis.VisList.VisList(output, source=ldf)
    # Ignore interestingness sorting since Generalize yields very few vis (preserve order of remove attribute, then remove filters)
    # for vis in vlist:
    # 	vis.score = interestingness(vis,ldf)

    vlist.remove_duplicates()
    vlist.sort(remove_invalid=True)
    vlist._collection = list(filter(lambda x: x.score != -1, vlist._collection))
    recommendation["collection"] = vlist
    return recommendation
