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
    for c in ldf.columns:
        if ldf.data_type[c] == "temporal":
            try:
                generated_vis = create_vis(ldf, c)
                visuals.extend(generated_vis)
            except (ValueError, AttributeError):
                pass
    recommendation = {
        "action": "Temporal",
        "description": "Show trends over <p class='highlight-descriptor'>time-related</p> attributes.",
    }
    # Doesn't make sense to generate a line chart if there is less than 3 datapoints (pre-aggregated)
    if len(ldf) < 3:
        recommendation["collection"] = []
        return recommendation
    vlist = VisList(visuals)
    vlist.sort()
    recommendation["collection"] = vlist
    return recommendation


def create_vis(ldf, col):
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
    visuals = []
    converted_string = ldf[col].astype(str)
    if converted_string.str.contains("-").any():
        parsed_date = converted_string.str.extract(r"([0-9]{4})?-?([0-9]{2})?-?([0-9]{1,2})?")
        valid_year, valid_month, valid_day = parsed_date.apply(lambda x: not x.isnull().all()).values

        date_vis = Vis([lux.Clause(col, data_type="temporal")], source=ldf, score=4)
        visuals.append(date_vis)

        # If date components (year, month, day) were parsed, create individuals visualizations for each
        if valid_year:
            year_col = col + " (year)"
            year_df = LuxDataFrame(
                {year_col: pd.to_datetime(parsed_date[0], format="%Y").dt.strftime("%Y")}
            )
            year_vis = Vis([lux.Clause(year_col, data_type="temporal")], source=year_df, score=3)
            visuals.append(year_vis)
        if valid_month:
            month_col = col + " (month)"
            month_df = LuxDataFrame(
                {month_col: pd.to_datetime(parsed_date[1], format="%m").dt.strftime("%m")}
            )
            month_vis = Vis([lux.Clause(month_col, data_type="temporal")], source=month_df, score=2)
            visuals.append(month_vis)
        if valid_day:
            day_col = col + " (day)"
            day_df = LuxDataFrame(
                {day_col: pd.to_datetime(parsed_date[2], format="%d").dt.strftime("%d")}
            )
            day_vis = Vis([lux.Clause(day_col, data_type="temporal")], source=day_df, score=1)
            visuals.append(day_vis)
    else:
        single_vis = Vis([lux.Clause(col, data_type="temporal")], source=ldf, score=5)
        visuals.append(single_vis)
    return visuals
