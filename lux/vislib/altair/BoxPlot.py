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
    def __init__(self, vis):
        super().__init__(vis)

    def __repr__(self):
        return f"BoxPlot <{str(self.vis)}>"

    def initialize_chart(self):

        x_attr = self.vis.get_attr_by_channel("x")[0]
        y_attr = self.vis.get_attr_by_channel("y")[0]

        x_attr_abv = str(x_attr.attribute)
        y_attr_abv = str(y_attr.attribute)

        k = 6
        self._topkcode = ""
        n_bars = len(self.data[x_attr_abv].unique())

        sort_order = self.data._order.get(x_attr_abv, [])

        text, topkcode = "", ""
        if n_bars > k:
            remaining_bars = n_bars - k

            self.data = self.data[(self.data[x_attr_abv].isin(sort_order[:k]))]
            # self.data = self.data.sort_values(columns=x_attr_abv, key=lambda x: sort_order.index(x)).head(k)
            text = alt.Chart(self.data).mark_text(
                x=155,
                y=142,
                align="right",
                color="#ff8e04",
                fontSize=11,
                text=f"+ {remaining_bars} more ...",
            )
            topkcode = f"""text = alt.Chart(visData).mark_text(
			x=155, 
			y=142,
			align="right",
			color = "#ff8e04",
			fontSize = 11,
			text=f"+ {remaining_bars} more ..."
		)
		chart = chart + text\n"""

        self.data = AltairChart.sanitize_dataframe(self.data)

        chart = (
            alt.Chart(self.data)
            .mark_boxplot(outliers=alt.MarkConfig(filled=True))
            .encode(x=alt.X(f"{y_attr_abv}:Q"), y=alt.Y(f"{x_attr_abv}:O", sort=sort_order))
        )
        if text != "":
            chart += text

        #####################################
        ## Constructing Altair Code String ##
        #####################################

        self.code += "import altair as alt\n"
        dfname = "placeholder_variable"
        self.code += f"""chart = alt.Chart({dfname}).mark_boxplot().encode(
            x={x_attr_abv}:O,
            y={y_attr_abv}:Q
            """
        self.code += topkcode

        return chart
