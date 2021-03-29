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


class Heatmap(MatplotlibChart):
    """
    Heatmap is a subclass of MatplotlibChart that render as a heatmap.
    All rendering properties for heatmap are set here.

    See Also
    --------
    matplotlib.org
    """

    def __init__(self, vis, fig, ax):
        super().__init__(vis, fig, ax)

    def __repr__(self):
        return f"Heatmap <{str(self.vis)}>"

    def initialize_chart(self):
        # return NotImplemented
        x_attr = self.vis.get_attr_by_channel("x")[0]
        y_attr = self.vis.get_attr_by_channel("y")[0]

        x_attr_abv = x_attr.attribute
        y_attr_abv = y_attr.attribute

        if len(x_attr.attribute) > 25:
            x_attr_abv = x_attr.attribute[:15] + "..." + x_attr.attribute[-10:]
        if len(y_attr.attribute) > 25:
            y_attr_abv = y_attr.attribute[:15] + "..." + y_attr.attribute[-10:]

        df = self.data

        plot_code = ""
        color_attr = self.vis.get_attr_by_channel("color")
        color_attr_name = ""
        color_map = "Blues"
        if len(color_attr) == 1:
            self.fig, self.ax = matplotlib_setup(6, 4)
            color_attr_name = color_attr[0].attribute
            df = pd.pivot_table(data=df, index="xBinStart", values=color_attr_name, columns="yBinStart")
            color_map = "viridis"
            plot_code += f"""df = pd.pivot_table(
                data=df, 
                index='xBinStart', 
                values='{color_attr_name}', 
                columns='yBinStart')\n"""
        else:
            df = pd.pivot_table(data=df, index="xBinStart", values="count", columns="yBinStart")
            df = df.apply(lambda x: np.log(x), axis=1)
            plot_code += f"""df = pd.pivot_table(
                    df, 
                    index='xBinStart', 
                    values='count', 
                    columns='yBinStart')\n"""
            plot_code += f"df = df.apply(lambda x: np.log(x), axis=1)\n"
        df = df.values

        plt.imshow(df, cmap=color_map)
        self.ax.set_aspect("auto")
        plt.gca().invert_yaxis()

        colorbar_code = ""
        if len(color_attr) == 1:
            cbar = plt.colorbar(label=color_attr_name)
            cbar.outline.set_linewidth(0)
            colorbar_code += f"cbar = plt.colorbar(label='{color_attr_name}')\n"
            colorbar_code += f"cbar.outline.set_linewidth(0)\n"

        self.ax.set_xlabel(x_attr_abv)
        self.ax.set_ylabel(y_attr_abv)
        self.ax.grid(False)

        self.code += "import numpy as np\n"
        self.code += "from math import nan\n"
        self.code += f"df = pd.DataFrame({str(self.data.to_dict())})\n"

        self.code += plot_code
        self.code += f"df = df.values\n"

        self.code += f"fig, ax = plt.subplots()\n"
        self.code += f"plt.imshow(df, cmap='{color_map}')\n"
        self.code += f"ax.set_aspect('auto')\n"
        self.code += f"plt.gca().invert_yaxis()\n"

        self.code += colorbar_code

        self.code += f"ax.set_xlabel('{x_attr_abv}')\n"
        self.code += f"ax.set_ylabel('{y_attr_abv}')\n"
        self.code += f"ax.grid(False)\n"
