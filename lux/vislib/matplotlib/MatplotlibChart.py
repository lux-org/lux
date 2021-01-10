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


class MatplotlibChart:
    """
    MatplotlibChart is a representation of a chart.
    Common utilities for charts that is independent of chart types should go here.

    See Also
    --------
    https://matplotlib.org/

    """

    def __init__(self, vis, fig, ax):
        self.vis = vis
        self.data = vis.data
        self.tooltip = True
        self.fig = fig
        self.ax = ax
        # ----- START self.code modification -----
        self.code = ""
        self.initialize_chart()
        # self.add_tooltip()
        # self.encode_color()
        self.add_title()
        # self.apply_default_config()

        # ----- END self.code modification -----

    def __repr__(self):
        return f"MatplotlibChart <{str(self.vis)}>"

    def add_tooltip(self):
        return NotImplemented

    def apply_default_config(self):
        return NotImplemented

    def encode_color(self):
        return NotImplemented

    def add_title(self):
        chart_title = self.vis.title
        if chart_title:
            self.ax.set_title(chart_title)

    def initialize_chart(self):
        return NotImplemented
