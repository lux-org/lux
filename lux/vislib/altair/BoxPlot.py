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

from lux.vislib.altair.AltairChart import AltairChart
import altair as alt

alt.data_transformers.disable_max_rows()


class BoxPlot(AltairChart):
    """
    BoxPlot yo
    """

    def __init__(self, vis):
        super().__init__(vis)

    def __repr__(self):
        return f"Boxplot <{str(self.vis)}>"

    def apply_default_config(self):
        super(BoxPlot, self).apply_default_config()
        self.chart = self.chart.properties(width=80, height=150)

    def initialize_chart(self):
        # return NotImplemented
        # x_attr = self.vis.get_attr_by_channel("x")[0]
        y_attr = self.vis.get_attr_by_channel("y")[0]

        # x_attr_abv = str(x_attr.attribute)
        y_attr_abv = str(y_attr.attribute)

        # if len(x_attr_abv) > 25:
        #     x_attr_abv = x_attr.attribute[:15] + "..." + x_attr.attribute[-10:]
        if len(y_attr_abv) > 25:
            y_attr_abv = y_attr.attribute[:15] + "..." + y_attr.attribute[-10:]

        # if isinstance(x_attr.attribute, str):
        #     x_attr.attribute = x_attr.attribute.replace(".", "")
        if isinstance(y_attr.attribute, str):
            y_attr.attribute = y_attr.attribute.replace(".", "")

        chart = (
            alt.Chart(self.data)
            .mark_boxplot()
            .encode(
                y=alt.Y(
                    y_attr.attribute,
                    type="quantitative",
                    axis=alt.Axis(title=y_attr_abv),
                ),
            )
        )
        # Setting tooltip as non-null
        # chart = chart.configure_mark(tooltip=alt.TooltipContent("encoding"))
        chart = chart.interactive()  # Enable Zooming and Panning

        ####################################
        # Constructing Altair Code String ##
        ####################################

        self.code += "import altair as alt\n"
        # self.code += f"visData = pd.DataFrame({str(self.data.to_dict(orient='records'))})\n"
        self.code += f"visData = pd.DataFrame({str(self.data.to_dict())})\n"
        self.code += f"""
		chart = alt.Chart(visData).mark_boxplot().encode(
			y=alt.Y({y_attr.attribute}, type='quantitative', axis=alt.Axis(title='{y_attr_abv}'))
		)
		chart = chart.interactive() # Enable Zooming and Panning
		"""
        return chart
