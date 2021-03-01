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
from lux.vis.VisList import VisList
from lux.vis.Vis import Vis
import pandas as pd
from lux.core.frame import LuxDataFrame
from lux.utils.date_utils import compute_date_granularity
from lux.interestingness.interestingness import interestingness
from lux.utils import utils


def temporal(ldf):
    """
    Generates line charts for temporal fields at different granularities.

    Parameters
    ----------
    ldf : lux.core.frame
            LuxDataFrame with underspecified intent.

    Returns
    -------
    recommendations : Dict[str,obj]
            Object with a collection of visualizations that result from the Temporal action.
    """
    visuals = []
    recommendation = {
        "action": "Temporal",
        "description": "Show trends over <p class='highlight-descriptor'>time-related</p> attributes.",
        "long_description": "Temporal displays line charts for all attributes related to datetimes in the dataframe.",
    }

    for c in ldf.columns:
        if ldf.data_type[c] == "temporal":
            try:
                generated_vis = create_temporal_vis(ldf, c)
                visuals.extend(generated_vis)
            except (ValueError, AttributeError, KeyError):
                pass

    # If no temporal visualizations were generated via parsing datetime, fallback to default behavior.
    if len(visuals) == 0:
        intent = [lux.Clause("?", data_type="temporal")]
        intent.extend(utils.get_filter_specs(ldf._intent))
        vlist = VisList(intent, ldf)
        for vis in vlist:
            vis.score = interestingness(vis, ldf)
    else:
        vlist = VisList(visuals)
        recommendation["long_description"] += (
            " The scoring will display all overall visualizations first,"
            + "all the (year) visualizations second, all the (month) visualizations third, and finally all the (day) visualizations."
        )

    # Doesn't make sense to generate a line chart if there is less than 3 datapoints (pre-aggregated)
    if len(ldf) < 3:
        recommendation["collection"] = []
        return recommendation
    vlist.sort()
    recommendation["collection"] = vlist
    return recommendation


def create_temporal_vis(ldf, col):
    """
    Creates and populates Vis objects for the different time-scale visualizations of the provided temporal column.

    Parameters
    ----------
    ldf : lux.core.frame
            LuxDataFrame with underspecified intent.

    col : str
            Name of temporal column.

    Returns
    -------
    visuals : [Vis]
            Collection of Vis objects.
    """
    formatted_date = pd.to_datetime(ldf[col], format="%Y-%m-%d")

    overall_vis = Vis([lux.Clause(col, data_type="temporal")], source=ldf, score=4)

    year_col = col + " (year)"
    year_df = LuxDataFrame({year_col: pd.to_datetime(formatted_date.dt.year, format="%Y")})
    year_vis = Vis([lux.Clause(year_col, data_type="temporal")], source=year_df, score=3)

    month_col = col + " (month)"
    month_df = LuxDataFrame({month_col: pd.to_datetime(formatted_date.dt.month, format="%m")})
    month_vis = Vis([lux.Clause(month_col, data_type="temporal")], source=month_df, score=2)

    day_col = col + " (day)"
    day_df = LuxDataFrame({day_col: pd.to_datetime(formatted_date.dt.day, format="%d")})
    day_vis = Vis([lux.Clause(day_col, data_type="temporal")], source=day_df, score=1)

    date_granularity = compute_date_granularity(formatted_date)
    unique_year_values = len(year_df[year_col].unique())
    unique_month_values = len(month_df[month_col].unique())
    visuals = []

    if date_granularity == "year":
        visuals.append(overall_vis)
    elif date_granularity == "month":
        if unique_year_values != 1:
            visuals.append(year_vis)
        if len(visuals) != 0:
            visuals.extend([overall_vis, month_vis])
        else:
            visuals.append(overall_vis)
    elif date_granularity == "day":
        if unique_year_values != 1:
            visuals.append(year_vis)
        if unique_month_values != 1:
            visuals.append(month_vis)
        if len(visuals) != 0:
            visuals.extend([overall_vis, day_vis])
        else:
            visuals.append(overall_vis)
    return visuals
