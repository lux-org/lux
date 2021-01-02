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
from typing import Callable
from lux.vislib.matplotlib.BarChart import BarChart
from lux.vislib.matplotlib.ScatterChart import ScatterChart
from lux.vislib.matplotlib.LineChart import LineChart
from lux.vislib.matplotlib.Histogram import Histogram
# from lux.vislib.altair.Heatmap import Heatmap

import matplotlib.pyplot as plt


class MatplotlibRenderer:
    """
    Renderer for Charts based on Altair (https://altair-viz.github.io/)
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
        # # Lazy Evaluation for 2D Binning
        # if vis.mark == "scatter" and vis._postbin:
        #     vis._mark = "heatmap"
        #     from lux.executor.PandasExecutor import PandasExecutor

        #     PandasExecutor.execute_2D_binning(vis)
        # # If a column has a Period dtype, or contains Period objects, convert it back to Datetime
        # if vis.data is not None:
        #     for attr in list(vis.data.columns):
        #         if pd.api.types.is_period_dtype(vis.data.dtypes[attr]) or isinstance(
        #             vis.data[attr].iloc[0], pd.Period
        #         ):
        #             dateColumn = vis.data[attr]
        #             vis.data[attr] = pd.PeriodIndex(dateColumn.values).to_timestamp()
        #         if pd.api.types.is_interval_dtype(vis.data.dtypes[attr]) or isinstance(
        #             vis.data[attr].iloc[0], pd.Interval
        #         ):
        #             vis.data[attr] = vis.data[attr].astype(str)
        #         if "." in attr:
        #             attr_clause = vis.get_attr_by_attr_name(attr)[0]
        #             # Suppress special character ".", not displayable in Altair
        #             # attr_clause.attribute = attr_clause.attribute.replace(".", "")
        #             vis._vis_data = vis.data.rename(columns={attr: attr.replace(".", "")})
        if vis.mark == "histogram":
            chart = Histogram(vis)
        elif vis.mark == "bar":
            chart = BarChart(vis)
        elif vis.mark == "scatter":
            chart = ScatterChart(vis)
        elif vis.mark == "line":
            chart = LineChart(vis)
        # elif vis.mark == "heatmap":
        #     chart = Heatmap(vis)
        else:
            chart = None
            return chart
        if chart:
            return {'config': chart.chart, 'vislib': 'matplotlib'}
        # # Test visualization
        # import numpy as np
        # import matplotlib.pyplot as plt

        # vis_data = [{'Q1': '18-21', 'Record': 2558},
        #             {'Q1': '22-24', 'Record': 2851},
        #             {'Q1': '25-29', 'Record': 3018},
        #             {'Q1': '30-34', 'Record': 2082},
        #             {'Q1': '35-39', 'Record': 1522},
        #             {'Q1': '40-44', 'Record': 1041},
        #             {'Q1': '45-49', 'Record': 746},
        #             {'Q1': '50-54', 'Record': 527},
        #             {'Q1': '55-59', 'Record': 315},
        #             {'Q1': '60-69', 'Record': 312},
        #             {'Q1': '70+', 'Record': 55}]
        # df = pd.DataFrame(vis_data)

        # objects = df["Q1"]
        # y_pos = np.arange(len(objects))
        # performance = df["Record"]

        # fig, ax = plt.subplots()
        # ax.bar(y_pos, performance, align='center', alpha=0.5)
        # ax.set_xticks(y_pos)
        # ax.set_xticklabels(objects)
        # ax.set_ylabel('Usage')
        # ax.set_title('Age of Data Scientists')

        # # Convert chart to HTML
        # import base64
        # from io import BytesIO
        # tmpfile = BytesIO()
        # fig.savefig(tmpfile, format='png')
        # chart_code = base64.b64encode(tmpfile.getvalue()).decode('utf-8') 
        # # Inside chartGallery.tsx change VegaLite component to be adaptable to different rendering mechanism (e.g, img)
        # # '<img src=\'data:image/png;base64,{}\'>
        # return {'config': chart_code, 'vislib': 'matplotlib'}

