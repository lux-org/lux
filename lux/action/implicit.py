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

from lux.vis.VisList import VisList
from lux.vis.Vis import Vis
import lux
import itertools
import numpy as np

def implicit_vis(ldf):
    """
    Generates bar chart distributions of different attributes in the dataframe.

    Parameters
    ----------
    ldf : lux.core.frame
            LuxDataFrame with underspecified intent.

    Returns
    -------
    recommendations : Dict[str,obj]
            object with a collection of visualizations that result from the Distribution action.
    """

    col_names = lux.config.code_tracker.get_implicit_intent()

    if col_names: 
        # make sure columns are in this df! 
        col_names = [c for c in col_names if (c in ldf.columns)]

        i_vis_list = []

        # first get univariate dists
        for col in col_names:
            vis = Vis( [lux.Clause(col)] )
            i_vis_list.append(vis)
        
        # then bimodal 
        for col_one, col_two in itertools.combinations(col_names, 2):
            vis = Vis( [ lux.Clause(col_one), lux.Clause(col_two) ] )
            i_vis_list.append(vis)
            
        lux_vis = VisList(i_vis_list, ldf)
    
    else:
        lux_vis = []

    numeric_cols = list(ldf.select_dtypes(include= np.number).columns)
    
    # for vis in i_vis_list:
    #     vis.score = interestingness(vis, ldf)
    # vlist.sort()

    recommendation = {
        "action": "Implicit",
        "description": "Show visualizations based off your recent <p class='highlight-descriptor'>code history</p>.",
        "long_description": """Implicit displays charts based off of your recent <b>code</b> analysis. \n
        Lux analyzes the code you have been writing in jupyter then looks for functions, columns, 
        etc that you have been accessing or manipulating to provide recommendations.""",
        "collection": lux_vis
    }
    
    return recommendation
