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

from lux.vislib.matplotlib.MatplotlibChart import MatplotlibChart
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lux.utils.utils import get_agg_title
import altair as alt
from lux.utils.utils import matplotlib_setup


class LineChart(MatplotlibChart):
    """
    LineChart is a subclass of MatplotlibChart that render as a line charts.
    All rendering properties for line charts are set here.

    See Also
    --------
    matplotlib.org
    """

    def __init__(self, dobj, fig, ax):
        super().__init__(dobj, fig, ax)

    def __repr__(self):
        return f"Line Chart <{str(self.vis)}>"

    def initialize_chart(self):
        self.tooltip = False  # tooltip looks weird for line chart
        x_attr = self.vis.get_attr_by_channel("x")[0]
        y_attr = self.vis.get_attr_by_channel("y")[0]

        x_attr_abv = x_attr.attribute
        y_attr_abv = y_attr.attribute

        if len(x_attr.attribute) > 25:
            x_attr_abv = x_attr.attribute[:15] + "..." + x_attr.attribute[-10:]
        if len(y_attr.attribute) > 25:
            y_attr_abv = y_attr.attribute[:15] + "..." + y_attr.attribute[-10:]

        self.data = self.data.dropna(subset=[x_attr.attribute, y_attr.attribute])

        df = self.data

        x_pts = df[x_attr.attribute]
        y_pts = df[y_attr.attribute]

        plot_code = ""

        color_attr = self.vis.get_attr_by_channel("color")
        if len(color_attr) == 1:
            self.fig, self.ax = matplotlib_setup(6, 4)
            color_attr_name = color_attr[0].attribute
            color_attr_type = color_attr[0].data_type
            colors = df[color_attr_name].values
            unique = list(set(colors))
            d_x = {}
            d_y = {}
            for i in unique:
                d_x[i] = []
                d_y[i] = []
            for i in range(len(colors)):
                d_x[colors[i]].append(x_pts[i])
                d_y[colors[i]].append(y_pts[i])
            for i in range(len(unique)):
                self.ax.plot(d_x[unique[i]], d_y[unique[i]], label=unique[i])
                plot_code += f"""ax.plot(
                        {d_x}[{unique}[{i}]], 
                        {d_y}[{unique}[{i}]], 
                        label={unique}[{i}])\n"""
            self.ax.legend(
                title=color_attr_name, bbox_to_anchor=(1.05, 1), loc="upper left", ncol=1, frameon=False
            )
            plot_code += f"""ax.legend(
                title='{color_attr_name}', 
                bbox_to_anchor=(1.05, 1), 
                loc='upper left', 
                ncol=1, 
                frameon=False,)\n"""
        else:
            self.ax.plot(x_pts, y_pts)
            plot_code += f"ax.plot(x_pts, y_pts)\n"

        x_label = ""
        y_label = ""
        if y_attr.data_model == "measure":
            agg_title = get_agg_title(y_attr)
            self.ax.set_xlabel(x_attr_abv)
            self.ax.set_ylabel(agg_title)
            x_label = x_attr_abv
            y_label = agg_title
        else:
            agg_title = get_agg_title(x_attr)
            self.ax.set_xlabel(agg_title)
            self.ax.set_ylabel(y_attr_abv)
            x_label = agg_title
            y_label = y_attr_abv

        self.code += "import numpy as np\n"
        self.code += "from math import nan\n"

        self.code += f"fig, ax = plt.subplots()\n"
        self.code += f"x_pts = df['{x_attr.attribute}']\n"
        self.code += f"y_pts = df['{y_attr.attribute}']\n"

        self.code += plot_code

        self.code += f"ax.set_xlabel('{x_label}')\n"
        self.code += f"ax.set_ylabel('{y_label}')\n"
