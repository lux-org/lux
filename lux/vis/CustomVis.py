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

from typing import List, Callable, Union
from lux.vis.Clause import Clause
from lux.utils.utils import check_import_lux_widget
import lux
import warnings

class CustomVis:
    """
    Vis Object represents a collection of fully fleshed out specifications required for data fetching and visualization.
    """

    def __init__(self, altChart):
        self.chart = altChart
        self.score = 1
        self.apply_default_config()
        
    def _repr_html_(self):
        from IPython.display import display

        check_import_lux_widget()
        import luxwidget

        from lux.core.frame import LuxDataFrame

        lux.config.code_tracker.analyze_recent_code()

        widget = luxwidget.LuxWidget(
            currentVis= self.to_code(),
            recommendations=[],
            intent="",
            message="",
        )
        display(widget)
    
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
        self.chart = self.chart.properties(width=160, height=150)
        # self.code += (
        #     "\nchart = chart.configure_title(fontWeight=500,fontSize=13,font='Helvetica Neue')\n"
        # )
        # self.code += "chart = chart.configure_axis(titleFontWeight=500,titleFontSize=11,titleFont='Helvetica Neue',\n"
        # self.code += "\t\t\t\t\tlabelFontWeight=400,labelFontSize=8,labelFont='Helvetica Neue',labelColor='#505050')\n"
        # self.code += "chart = chart.configure_legend(titleFontWeight=500,titleFontSize=10,titleFont='Helvetica Neue',\n"
        # self.code += "\t\t\t\t\tlabelFontWeight=400,labelFontSize=8,labelFont='Helvetica Neue')\n"
        # self.code += "chart = chart.properties(width=160,height=150)\n"


    def to_code(self, language="vegalite", **kwargs):
        """
        Export Vis object to code specification

        Parameters
        ----------
        language : str, optional
            choice of target language to produce the visualization code in, by default "vegalite"

        Returns
        -------
        spec:
            visualization specification corresponding to the Vis object
        """
        if lux.config.plotting_style and (
                lux.config.plotting_backend == "vegalite" or lux.config.plotting_backend == "altair"
            ):
            chart = lux.config.plotting_style(self.chart)
        else:
            chart = self.chart

        chart_dict = chart.to_dict()
        chart_dict["vislib"] = "vegalite"
        return chart_dict


