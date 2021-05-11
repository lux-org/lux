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
from lux.utils.utils import matplotlib_setup
from matplotlib.cm import ScalarMappable


class ScatterChart(MatplotlibChart):
    """
    ScatterChart is a subclass of MatplotlibChart that render as a scatter charts.
    All rendering properties for scatter charts are set here.

    See Also
    --------
    matplotlib.org
    """

    def __init__(self, vis, fig, ax):
        super().__init__(vis, fig, ax)

    def __repr__(self):
        return f"ScatterChart <{str(self.vis)}>"

    def initialize_chart(self):
        x_attr = self.vis.get_attr_by_channel("x")[0]
        y_attr = self.vis.get_attr_by_channel("y")[0]

        x_attr_abv = x_attr.attribute
        y_attr_abv = y_attr.attribute

        if len(x_attr.attribute) > 25:
            x_attr_abv = x_attr.attribute[:15] + "..." + x_attr.attribute[-10:]
        if len(y_attr.attribute) > 25:
            y_attr_abv = y_attr.attribute[:15] + "..." + y_attr.attribute[-10:]

        df = self.data.dropna()

        x_pts = df[x_attr.attribute]
        y_pts = df[y_attr.attribute]

        set_fig_code = ""
        plot_code = ""

        color_attr = self.vis.get_attr_by_channel("color")
        if len(color_attr) == 1:
            color_attr_name = color_attr[0].attribute
            color_attr_type = color_attr[0].data_type
            colors = df[color_attr_name].values
            plot_code += f"colors = df['{color_attr_name}'].values\n"
            unique = list(set(colors))
            vals = [unique.index(i) for i in colors]
            if color_attr_type == "quantitative":
                self.fig, self.ax = matplotlib_setup(7, 5)
                set_fig_code = "fig, ax = plt.subplots(figsize=(7, 5))\n"
                self.ax.scatter(x_pts, y_pts, c=vals, cmap="Blues", alpha=0.5)
                plot_code += f"ax.scatter(x_pts, y_pts, c={vals}, cmap='Blues', alpha=0.5)\n"
                my_cmap = plt.cm.get_cmap("Blues")
                max_color = max(colors)
                sm = ScalarMappable(cmap=my_cmap, norm=plt.Normalize(0, max_color))
                sm.set_array([])

                cbar = plt.colorbar(sm, label=color_attr_name)
                cbar.outline.set_linewidth(0)
                plot_code += f"my_cmap = plt.cm.get_cmap('Blues')\n"
                plot_code += f"""sm = ScalarMappable(
                    cmap=my_cmap, 
                    norm=plt.Normalize(0, {max_color}))\n"""

                plot_code += f"cbar = plt.colorbar(sm, label='{color_attr_name}')\n"
                plot_code += f"cbar.outline.set_linewidth(0)\n"
            else:
                if len(unique) >= 16:
                    unique = unique[:16]

                maxlen = 0
                for i in range(len(unique)):
                    unique[i] = str(unique[i])
                    if len(unique[i]) > 26:
                        unique[i] = unique[i][:26] + "..."
                    if len(unique[i]) > maxlen:
                        maxlen = len(unique[i])
                if maxlen > 20:
                    self.fig, self.ax = matplotlib_setup(9, 5)
                    set_fig_code = "fig, ax = plt.subplots(figsize=(9, 5))\n"
                else:
                    self.fig, self.ax = matplotlib_setup(7, 5)
                    set_fig_code = "fig, ax = plt.subplots(figsize=(7, 5))\n"

                cmap = "Set1"
                if len(unique) > 9:
                    cmap = "tab20c"
                scatter = self.ax.scatter(x_pts, y_pts, c=vals, cmap=cmap)
                plot_code += f"scatter = ax.scatter(x_pts, y_pts, c={vals}, cmap={cmap})\n"

                leg = self.ax.legend(
                    handles=scatter.legend_elements(num=range(0, len(unique)))[0],
                    labels=unique,
                    title=color_attr_name,
                    markerscale=2.0,
                    bbox_to_anchor=(1.05, 1),
                    loc="upper left",
                    ncol=1,
                    frameon=False,
                    fontsize="13",
                )
                scatter.set_alpha(0.5)
                plot_code += f"""ax.legend(
                    handles=scatter.legend_elements(num=range(0, len({unique})))[0],
                    labels={unique},
                    title='{color_attr_name}', 
                    markerscale=2.,
                    bbox_to_anchor=(1.05, 1), 
                    loc='upper left', 
                    ncol=1, 
                    frameon=False,
                    fontsize='13')\n"""
                plot_code += "scatter.set_alpha(0.5)\n"
        else:
            set_fig_code = "fig, ax = plt.subplots(figsize=(4.5, 4))\n"
            self.ax.scatter(x_pts, y_pts, alpha=0.5)
            plot_code += f"ax.scatter(x_pts, y_pts, alpha=0.5)\n"
        self.ax.set_xlabel(x_attr_abv, fontsize="15")
        self.ax.set_ylabel(y_attr_abv, fontsize="15")

        self.code += "import numpy as np\n"
        self.code += "from math import nan\n"
        self.code += "from matplotlib.cm import ScalarMappable\n"

        self.code += set_fig_code
        self.code += f"x_pts = df['{x_attr.attribute}']\n"
        self.code += f"y_pts = df['{y_attr.attribute}']\n"

        self.code += plot_code
        self.code += f"ax.set_xlabel('{x_attr_abv}', fontsize='15')\n"
        self.code += f"ax.set_ylabel('{y_attr_abv}', fontsize='15')\n"
