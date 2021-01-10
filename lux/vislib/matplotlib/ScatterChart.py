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
        
        df = pd.DataFrame(self.data)

        x_pts = df[x_attr.attribute]
        y_pts = df[y_attr.attribute]

        color_attr = self.vis.get_attr_by_channel("color")
        if len(color_attr) == 1:
            self.fig, self.ax = matplotlib_setup(6,4)
            color_attr_name = color_attr[0].attribute
            color_attr_type = color_attr[0].data_type
            colors = df[color_attr_name].values
            unique = list(set(colors))
            vals = []
            for i in colors:
                vals.append(unique.index(i))
            if color_attr_type == "quantitative":
                scatter = self.ax.scatter(x_pts, y_pts, c=vals, cmap="Blues", alpha=0.5)
                my_cmap = plt.cm.get_cmap('Blues')
                sm = ScalarMappable(cmap=my_cmap, norm=plt.Normalize(0,max(colors)))
                sm.set_array([])

                cbar = plt.colorbar(sm, label=color_attr_name)
                cbar.outline.set_linewidth(0)
            else:
                scatter = self.ax.scatter(x_pts, y_pts, c=vals, alpha=0.5)
                unique = [str(i) for i in unique]
                self.ax.legend(handles=scatter.legend_elements(num=range(0, len(unique)))[0], labels=unique, title=color_attr_name, bbox_to_anchor=(1.05, 1), loc='upper left', ncol=1, frameon=False)
        else:
            self.ax.scatter(x_pts, y_pts, alpha=0.5)
        self.ax.set_xlabel(x_attr_abv)
        self.ax.set_ylabel(y_attr_abv)
        plt.tight_layout()

        self.code += "import matplotlib.pyplot as plt\n"
        self.code += "import numpy as np\n"
        self.code += "from math import nan\n"
        self.code += f"df = pd.DataFrame({str(self.data.to_dict())})\n"

        self.code += f"fig, ax = plt.subplots()\n"
        self.code += f"x_pts = df['{x_attr.attribute}']\n"
        self.code += f"y_pts = df['{y_attr.attribute}']\n"

        self.code += f"ax.scatter(x_pts, y_pts)\n"
        self.code += f"ax.set_xlabel('{x_attr_abv}')\n"
        self.code += f"ax.set_ylabel('{y_attr_abv}')\n"
        self.code += f"fig\n"
