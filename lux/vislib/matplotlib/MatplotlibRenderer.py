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
import pandas as pd
from lux.executor.PandasExecutor import PandasExecutor
from lux.vislib.matplotlib.BarChart import BarChart
from lux.vislib.matplotlib.ScatterChart import ScatterChart
from lux.vislib.matplotlib.LineChart import LineChart
from lux.vislib.matplotlib.Histogram import Histogram
from lux.vislib.matplotlib.Heatmap import Heatmap
from lux.vislib.altair.AltairRenderer import AltairRenderer
import matplotlib.pyplot as plt
from lux.utils.utils import matplotlib_setup

import base64
from io import BytesIO


class MatplotlibRenderer:
    """
    Renderer for Charts based on Matplotlib (https://matplotlib.org/)
    """

    def __init__(self, output_type="matplotlib"):
        self.output_type = output_type

    def __repr__(self):
        return f"MatplotlibRenderer"

    def create_vis(self, vis, standalone=True):
        """
        Input Vis object and return a visualization specification

        Parameters
        ----------
        vis: lux.vis.Vis
                Input Vis (with data)
        standalone: bool
                Flag to determine if outputted code uses user-defined variable names or can be run independently
        Returns
        -------
        chart : altair.Chart
                Output Altair Chart Object
        """
        # Lazy Evaluation for 2D Binning
        if vis.mark == "scatter" and vis._postbin:
            vis._mark = "heatmap"

            PandasExecutor.execute_2D_binning(vis)
        # If a column has a Period dtype, or contains Period objects, convert it back to Datetime
        if vis.data is not None:
            for attr in list(vis.data.columns):
                if pd.api.types.is_period_dtype(vis.data.dtypes[attr]) or isinstance(
                    vis.data[attr].iloc[0], pd.Period
                ):
                    dateColumn = vis.data[attr]
                    vis.data[attr] = pd.PeriodIndex(dateColumn.values).to_timestamp()
                if pd.api.types.is_interval_dtype(vis.data.dtypes[attr]) or isinstance(
                    vis.data[attr].iloc[0], pd.Interval
                ):
                    vis.data[attr] = vis.data[attr].astype(str)
        fig, ax = matplotlib_setup(4.5, 4)
        if vis.mark == "histogram":
            chart = Histogram(vis, fig, ax)
        elif vis.mark == "bar":
            chart = BarChart(vis, fig, ax)
        elif vis.mark == "scatter":
            chart = ScatterChart(vis, fig, ax)
        elif vis.mark == "line":
            chart = LineChart(vis, fig, ax)
        elif vis.mark == "heatmap":
            chart = Heatmap(vis, fig, ax)
        elif vis.mark == "geographical":
            return AltairRenderer().create_vis(vis, False)
        else:
            chart = None
            return chart
        if chart:
            plt.tight_layout()
            if lux.config.plotting_style and (
                lux.config.plotting_backend == "matplotlib"
                or lux.config.plotting_backend == "matplotlib_svg"
            ):
                chart.ax = lux.config.plotting_style(chart.fig, chart.ax)
            plt.tight_layout()
            tmpfile = BytesIO()
            chart.fig.savefig(tmpfile, format="png")
            chart.chart = base64.b64encode(tmpfile.getvalue()).decode("utf-8")
            plt.clf()
            plt.close("all")
            if self.output_type == "matplotlib_svg":
                return {"config": chart.chart, "vislib": "matplotlib"}
            if self.output_type == "matplotlib":
                if lux.config.plotting_style:
                    import inspect

                    chart.code += "\n".join(
                        inspect.getsource(lux.config.plotting_style).split("\n    ")[1:-1]
                    )
                chart.code += "\nfig"
                chart.code = chart.code.replace("\n\t\t", "\n")
                return chart.code
