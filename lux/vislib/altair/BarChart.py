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
from lux.utils.utils import get_agg_title


class BarChart(AltairChart):
    """
    BarChart is a subclass of AltairChart that render as a bar charts.
    All rendering properties for bar charts are set here.

    See Also
    --------
    altair-viz.github.io
    """

    def __init__(self, dobj):
        super().__init__(dobj)

    def __repr__(self):
        return f"Bar Chart <{str(self.vis)}>"

    def initialize_chart(self):
        self.tooltip = False
        x_attr = self.vis.get_attr_by_channel("x")[0]
        y_attr = self.vis.get_attr_by_channel("y")[0]

        x_attr_abv = str(x_attr.attribute)
        y_attr_abv = str(y_attr.attribute)

        if len(x_attr_abv) > 25:
            x_attr_abv = x_attr.attribute[:15] + "..." + x_attr.attribute[-10:]
        if len(y_attr_abv) > 25:
            y_attr_abv = y_attr.attribute[:15] + "..." + y_attr.attribute[-10:]
        if isinstance(x_attr.attribute, str):
            x_attr.attribute = x_attr.attribute.replace(".", "")
        if isinstance(y_attr.attribute, str):
            y_attr.attribute = y_attr.attribute.replace(".", "")

        if x_attr.data_model == "measure":
            agg_title = get_agg_title(x_attr)
            measure_attr = x_attr.attribute
            y_attr_field = alt.Y(
                str(y_attr.attribute),
                type=y_attr.data_type,
                axis=alt.Axis(labelOverlap=True, title=y_attr_abv),
            )
            x_attr_field = alt.X(
                str(x_attr.attribute),
                type=x_attr.data_type,
                title=agg_title,
                axis=alt.Axis(title=agg_title),
            )
            y_attr_field_code = f"alt.Y('{y_attr.attribute}', type= '{y_attr.data_type}', axis=alt.Axis(labelOverlap=True, title='{y_attr_abv}'))"
            x_attr_field_code = f"alt.X('{x_attr.attribute}', type= '{x_attr.data_type}', title='{agg_title}', axis=alt.Axis(title='{agg_title}'))"

            if y_attr.sort == "ascending":
                y_attr_field.sort = "-x"
                y_attr_field_code = f"alt.Y('{y_attr.attribute}', type= '{y_attr.data_type}', axis=alt.Axis(labelOverlap=True, title='{y_attr_abv}'), sort ='-x')"
        else:
            agg_title = get_agg_title(y_attr)
            measure_attr = y_attr.attribute
            x_attr_field = alt.X(
                str(x_attr.attribute),
                type=x_attr.data_type,
                axis=alt.Axis(labelOverlap=True, title=x_attr_abv),
            )
            x_attr_field_code = f"alt.X('{x_attr.attribute}', type= '{x_attr.data_type}', axis=alt.Axis(labelOverlap=True, title='{x_attr_abv}'))"
            y_attr_field = alt.Y(
                str(y_attr.attribute),
                type=y_attr.data_type,
                title=agg_title,
                axis=alt.Axis(title=agg_title),
            )
            y_attr_field_code = f"alt.Y('{y_attr.attribute}', type= '{y_attr.data_type}', title='{agg_title}', axis=alt.Axis(title='{agg_title}'))"
            if x_attr.sort == "ascending":
                x_attr_field.sort = "-y"
                x_attr_field_code = f"alt.X('{x_attr.attribute}', type= '{x_attr.data_type}', axis=alt.Axis(labelOverlap=True, title='{x_attr_abv}'),sort='-y')"
        k = 10
        self._topkcode = ""
        n_bars = len(self.data.iloc[:, 0].unique())

        if n_bars > k:  # Truncating to only top k
            remaining_bars = n_bars - k
            self.data = self.data.nlargest(k, columns=measure_attr)
            self.data = AltairChart.sanitize_dataframe(self.data)
            self.text = alt.Chart(self.data).mark_text(
                x=155,
                y=142,
                align="right",
                color="#ff8e04",
                fontSize=11,
                text=f"+ {remaining_bars} more ...",
            )

            self._topkcode = f"""text = alt.Chart(visData).mark_text(
			x=155, 
			y=142,
			align="right",
			color = "#ff8e04",
			fontSize = 11,
			text=f"+ {remaining_bars} more ..."
		)
		chart = chart + text\n"""
        self.data = AltairChart.sanitize_dataframe(self.data)
        chart = alt.Chart(self.data).mark_bar().encode(y=y_attr_field, x=x_attr_field)

        # TODO: tooltip messes up the count() bar charts
        # Can not do interactive whenever you have default count measure otherwise output strange error (Javascript Error: Cannot read property 'length' of undefined)
        # chart = chart.interactive() # If you want to enable Zooming and Panning

        self.code += "import altair as alt\n"
        # self.code += f"visData = pd.DataFrame({str(self.data.to_dict(orient='records'))})\n"
        self.code += f"visData = pd.DataFrame({str(self.data.to_dict())})\n"
        self.code += f"""
		chart = alt.Chart(visData).mark_bar().encode(
		    y = {y_attr_field_code},
		    x = {x_attr_field_code},
		)\n"""
        return chart

    def add_text(self):
        if self._topkcode != "":
            self.chart = self.chart + self.text
            self.code += self._topkcode

    # override encode_color in AltairChart to enforce add_text occurs afterwards
    def encode_color(self):
        AltairChart.encode_color(self)
        self.add_text()
        # Setting tooltip as non-null
        self.chart = self.chart.configure_mark(tooltip=alt.TooltipContent("encoding"))
        self.code += f"""chart = chart.configure_mark(tooltip=alt.TooltipContent('encoding'))"""
