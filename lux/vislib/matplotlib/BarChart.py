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
from lux.utils.utils import get_agg_title
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lux.utils.utils import matplotlib_setup
from matplotlib.cm import ScalarMappable
from lux.utils.date_utils import compute_date_granularity
from matplotlib.ticker import MaxNLocator


class BarChart(MatplotlibChart):
    """
    BarChart is a subclass of MatplotlibChart that render as a bar charts.
    All rendering properties for bar charts are set here.

    See Also
    --------
    matplotlib.org
    """

    def __init__(self, dobj, fig, ax):
        super().__init__(dobj, fig, ax)

    def __repr__(self):
        return f"Bar Chart <{str(self.vis)}>"

    def initialize_chart(self):
        self.tooltip = False
        x_attr = self.vis.get_attr_by_channel("x")[0]
        y_attr = self.vis.get_attr_by_channel("y")[0]

        x_attr_abv = x_attr.attribute
        y_attr_abv = y_attr.attribute

        if len(x_attr.attribute) > 25:
            x_attr_abv = x_attr.attribute[:15] + "..." + x_attr.attribute[-10:]
        if len(y_attr.attribute) > 25:
            y_attr_abv = y_attr.attribute[:15] + "..." + y_attr.attribute[-10:]

        if x_attr.data_model == "measure":
            agg_title = get_agg_title(x_attr)
            measure_attr = x_attr.attribute
            bar_attr = y_attr.attribute
        else:
            agg_title = get_agg_title(y_attr)
            measure_attr = y_attr.attribute
            bar_attr = x_attr.attribute

        k = 10
        n_bars = len(self.data.iloc[:, 0].unique())
        if n_bars > k:  # Truncating to only top k
            remaining_bars = n_bars - k
            self.data = self.data.nlargest(k, measure_attr)
            self.ax.text(
                0.95,
                0.01,
                f"+ {remaining_bars} more ...",
                verticalalignment="bottom",
                horizontalalignment="right",
                transform=self.ax.transAxes,
                fontsize=11,
                fontweight="bold",
                color="#ff8e04",
            )

        df = self.data

        bars = df[bar_attr].apply(lambda x: str(x))
        measurements = df[measure_attr]

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
                d_x[colors[i]].append(bars[i])
                d_y[colors[i]].append(measurements[i])
            for i in range(len(unique)):
                self.ax.barh(d_x[unique[i]], d_y[unique[i]], label=unique[i])
                plot_code += (
                    f"ax.barh({d_x}[{unique}[{i}]], {d_y}[{unique}[{i}]], label={unique}[{i}])\n"
                )
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
            self.ax.barh(bars, measurements, align="center")
            plot_code += f"ax.barh(bars, measurements, align='center')\n"

        y_ticks_abbev = df[bar_attr].apply(lambda x: str(x)[:10] + "..." if len(str(x)) > 10 else str(x))
        self.ax.set_yticks(bars)
        self.ax.set_yticklabels(y_ticks_abbev)

        self.ax.set_xlabel(x_attr_abv)
        self.ax.set_ylabel(y_attr_abv)
        plt.gca().invert_yaxis()

        self.code += "import numpy as np\n"
        self.code += "from math import nan\n"

        self.code += f"fig, ax = plt.subplots()\n"
        self.code += f"bars = df['{bar_attr}']\n"
        self.code += f"measurements = df['{measure_attr}']\n"

        self.code += plot_code

        self.code += f"ax.set_xlabel('{x_attr_abv}')\n"
        self.code += f"ax.set_ylabel('{y_attr_abv}')\n"
