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


class Histogram(MatplotlibChart):
    """
    Histogram is a subclass of AltairChart that render as a histograms.
    All rendering properties for histograms are set here.

    See Also
    --------
    matplotlib.org
    """

    def __init__(self, vis, fig, ax):
        super().__init__(vis, fig, ax)

    def __repr__(self):
        return f"Histogram <{str(self.vis)}>"

    def initialize_chart(self):
        self.tooltip = False
        measure = self.vis.get_attr_by_data_model("measure", exclude_record=True)[0]
        msr_attr = self.vis.get_attr_by_channel(measure.channel)[0]

        msr_attr_abv = msr_attr.attribute

        if len(msr_attr.attribute) > 17:
            msr_attr_abv = msr_attr.attribute[:10] + "..." + msr_attr.attribute[-7:]

        x_min = self.vis.min_max[msr_attr.attribute][0]
        x_max = self.vis.min_max[msr_attr.attribute][1]

        markbar = abs(x_max - x_min) / 12

        df = self.data

        bars = df[msr_attr.attribute]
        measurements = df["Number of Records"]

        self.ax.bar(bars, measurements, width=markbar)
        self.ax.set_xlim(x_min, x_max)

        x_label = ""
        y_label = ""
        axis_title = f"{msr_attr_abv} (binned)"
        if msr_attr_abv == " ":
            axis_title = "Series (binned)"
        if measure.channel == "x":
            x_label = axis_title
            y_label = "Number of Records"
        elif measure.channel == "y":
            x_label = "Number of Records"
            y_label = axis_title

        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)

        self.code += "import numpy as np\n"
        self.code += "from math import nan\n"
        self.code += f"df = pd.DataFrame({str(self.data.to_dict())})\n"

        self.code += f"fig, ax = plt.subplots()\n"
        self.code += f"bars = df['{msr_attr.attribute}']\n"
        self.code += f"measurements = df['Number of Records']\n"

        self.code += f"ax.bar(bars, measurements, width={markbar})\n"
        self.code += f"ax.set_xlabel('{x_label}')\n"
        self.code += f"ax.set_ylabel('{y_label}')\n"
