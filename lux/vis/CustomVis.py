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
import altair as alt
import warnings


class CustomVis:
    """
    Lightweight wrapper for altair charts to be plotted directly into the widget without intents or anything.

    TODO: add more property studs so this can be passed into VisList successfully,
    right now have to init an vislist then manually extend the collection
    """

    def __init__(self, intent, altChart, data, width=160, height=150, override_c_config=None):
        # local properties
        self._inferred_intent = intent
        self._intent = intent
        self.chart = altChart
        self.score = 0

        # @property copy from Vis
        self.data = data
        # self.code below
        self.intent = intent
        self.min_max = {}
        self.mark = ""

        # vis defaults
        self.chart_width = width
        self.chart_height = height

        # chart config
        base_chart_config = {"interactive": True, "tooltip": True}
        if override_c_config and isinstance(override_c_config, dict):
            base_chart_config.update(override_c_config)
        self.chart_config = base_chart_config

        if self.chart:
            self.apply_default_config()
            self.code = self.to_code()

    # def generate_code_str(self):
    #     self.code += "import altair as alt\n"
    #     ### self.code += f"visData = pd.DataFrame({str(self.data.to_dict(orient='records'))})\n"
    #     # self.code += f"visData = pd.DataFrame({str(self.data.to_dict())})\n"

    def _repr_html_(self):
        from IPython.display import display

        check_import_lux_widget()
        import luxwidget

        from lux.core.frame import LuxDataFrame

        widget = luxwidget.LuxWidget(
            currentVis=self.to_code(), recommendations=[], intent="", message="", history_list=[]
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
        self.chart = self.chart.properties(width=self.chart_width, height=self.chart_height)

        if self.chart_config["tooltip"]:
            self.chart = self.chart.configure_mark(tooltip=alt.TooltipContent("encoding"))

        if self.chart_config["interactive"]:
            self.chart = self.chart.interactive()  # Enable Zooming and Panning

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
        if self.chart is None:
            return None

        if lux.config.plotting_style and (
            lux.config.plotting_backend == "vegalite" or lux.config.plotting_backend == "altair"
        ):
            chart = lux.config.plotting_style(self.chart)
        else:
            chart = self.chart

        chart_dict = chart.to_dict()
        chart_dict["vislib"] = "vegalite"
        return chart_dict
