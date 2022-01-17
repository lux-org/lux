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

import pandas as pd
import numpy as np
import altair as alt
from lux.utils.date_utils import compute_date_granularity
import lux


class AltairChart:
    """
    AltairChart is a representation of a chart.
    Common utilities for charts that is independent of chart types should go here.

    See Also
    --------
    altair-viz.github.io

    """

    def __init__(self, vis):
        self.vis = vis
        self.data = vis.data
        self.tooltip = True
        # ----- START self.code modification -----
        self.code = ""
        self.width = 160
        self.height = 150
        self.chart = self.initialize_chart()
        # self.add_tooltip()
        self.encode_color()
        self.add_title()
        self.apply_default_config()

        # ----- END self.code modification -----

    def __repr__(self):
        return f"AltairChart <{str(self.vis)}>"

    def add_tooltip(self):
        if self.tooltip:
            self.chart = self.chart.encode(tooltip=list(self.vis.data.columns))

    def apply_default_config(self):
        self.chart = self.chart.configure_title(fontWeight=500, fontSize=13, font="Helvetica Neue")
        self.chart = self.chart.configure_axis(
            titleFontWeight=500,
            titleFontSize=11,
            titleFont="Helvetica Neue",
            labelFontWeight=400,
            labelFontSize=9,
            labelFont="Helvetica Neue",
            labelColor="#505050",
        )
        self.chart = self.chart.configure_legend(
            titleFontWeight=500,
            titleFontSize=10,
            titleFont="Helvetica Neue",
            labelFontWeight=400,
            labelFontSize=9,
            labelFont="Helvetica Neue",
        )
        plotting_scale = lux.config.plotting_scale
        self.chart = self.chart.properties(
            width=self.width * plotting_scale, height=self.height * plotting_scale
        )
        self.code += (
            "\nchart = chart.configure_title(fontWeight=500,fontSize=13,font='Helvetica Neue')\n"
        )
        self.code += "chart = chart.configure_axis(titleFontWeight=500,titleFontSize=11,titleFont='Helvetica Neue',\n"
        self.code += "\t\t\t\t\tlabelFontWeight=400,labelFontSize=8,labelFont='Helvetica Neue',labelColor='#505050')\n"
        self.code += "chart = chart.configure_legend(titleFontWeight=500,titleFontSize=10,titleFont='Helvetica Neue',\n"
        self.code += "\t\t\t\t\tlabelFontWeight=400,labelFontSize=8,labelFont='Helvetica Neue')\n"
        self.code += f"chart = chart.properties(width={self.width * plotting_scale},height={self.height  * plotting_scale})\n"

    def encode_color(self):
        color_attr = self.vis.get_attr_by_channel("color")
        if len(color_attr) == 1:
            color_attr_name = color_attr[0].attribute
            color_attr_type = color_attr[0].data_type
            if color_attr_type == "temporal":
                timeUnit = compute_date_granularity(self.vis.data[color_attr_name])
                self.chart = self.chart.encode(
                    color=alt.Color(
                        str(color_attr_name),
                        type=color_attr_type,
                        timeUnit=timeUnit,
                        title=color_attr_name,
                    )
                )
                self.code += f"chart = chart.encode(color=alt.Color('{color_attr_name}',type='{color_attr_type}',timeUnit='{timeUnit}',title='{color_attr_name}'))"
            else:
                self.chart = self.chart.encode(
                    color=alt.Color(str(color_attr_name), type=color_attr_type)
                )
                self.code += f"chart = chart.encode(color=alt.Color('{color_attr_name}',type='{color_attr_type}'))\n"
        elif len(color_attr) > 1:
            raise ValueError(
                "There should not be more than one attribute specified in the same channel."
            )

    def add_title(self):
        chart_title = self.vis.title
        if chart_title:
            self.chart = self.chart.encode().properties(title=chart_title)
            if self.code != "":
                self.code += f"chart = chart.encode().properties(title = '{chart_title}')"

    def initialize_chart(self):
        return NotImplemented

    @classmethod
    def sanitize_dataframe(self, df):
        for attr in df.columns:
            # Check if dtype is unrecognized by Altair (#247)
            if str(df[attr].dtype) == "Float64":
                df[attr] = df[attr].astype(np.float64)

            # Altair can not visualize non-string columns
            # convert all non-string columns in to strings
            df = df.rename(columns={attr: str(attr)})
        return df
