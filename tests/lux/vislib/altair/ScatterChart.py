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


class ScatterChart(AltairChart):
    """
    ScatterChart is a subclass of AltairChart that render as a scatter charts.
    All rendering properties for scatter charts are set here.

    See Also
    --------
    altair-viz.github.io
    """

    def __init__(self, vis):
        super().__init__(vis)

    def __repr__(self):
        return f"ScatterChart <{str(self.vis)}>"

    def initialize_chart(self):
        x_attr = self.vis.get_attr_by_channel("x")[0]
        y_attr = self.vis.get_attr_by_channel("y")[0]

        x_attr_abv = str(x_attr.attribute)
        y_attr_abv = str(y_attr.attribute)

        if len(x_attr_abv) > 25:
            x_attr_abv = x_attr.attribute[:15] + "..." + x_attr.attribute[-10:]
        if len(y_attr_abv) > 25:
            y_attr_abv = y_attr.attribute[:15] + "..." + y_attr.attribute[-10:]

        x_min = self.vis.min_max[x_attr.attribute][0]
        x_max = self.vis.min_max[x_attr.attribute][1]

        y_min = self.vis.min_max[y_attr.attribute][0]
        y_max = self.vis.min_max[y_attr.attribute][1]

        if isinstance(x_attr.attribute, str):
            x_attr.attribute = x_attr.attribute.replace(".", "")
        if isinstance(y_attr.attribute, str):
            y_attr.attribute = y_attr.attribute.replace(".", "")
        self.data = AltairChart.sanitize_dataframe(self.data)
        chart = (
            alt.Chart(self.data)
            .mark_circle()
            .encode(
                x=alt.X(
                    str(x_attr.attribute),
                    scale=alt.Scale(domain=(x_min, x_max)),
                    type=x_attr.data_type,
                    axis=alt.Axis(title=x_attr_abv),
                ),
                y=alt.Y(
                    str(y_attr.attribute),
                    scale=alt.Scale(domain=(y_min, y_max)),
                    type=y_attr.data_type,
                    axis=alt.Axis(title=y_attr_abv),
                ),
            )
        )
        # Setting tooltip as non-null
        chart = chart.configure_mark(tooltip=alt.TooltipContent("encoding"))
        chart = chart.interactive()  # Enable Zooming and Panning

        #####################################
        ## Constructing Altair Code String ##
        #####################################

        self.code += "import altair as alt\n"
        dfname = "placeholder_variable"
        self.code += f"""
		chart = alt.Chart({dfname}).mark_circle().encode(
		    x=alt.X('{x_attr.attribute}',scale=alt.Scale(domain=({x_min}, {x_max})),type='{x_attr.data_type}', axis=alt.Axis(title='{x_attr_abv}')),
		    y=alt.Y('{y_attr.attribute}',scale=alt.Scale(domain=({y_min}, {y_max})),type='{y_attr.data_type}', axis=alt.Axis(title='{y_attr_abv}'))
		)
		chart = chart.configure_mark(tooltip=alt.TooltipContent('encoding')) # Setting tooltip as non-null
		chart = chart.interactive() # Enable Zooming and Panning
		"""
        return chart
