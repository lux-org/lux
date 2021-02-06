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


class SymbolMap(AltairChart):
    """
    SymbolMap is a subclass of AltairChart that renders proportional symbol maps.
    All rendering properties for proportional symbol maps are set here.

    See Also
    --------
    altair-viz.github.io
    """

    def __init__(self, dobj):
        super().__init__(dobj)

    def __repr__(self):
        return f"Proportional Symbol Map <{str(self.vis)}>"

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

        secondary_feature = self.get_secondary_feature()
        background = self.get_background(secondary_feature)
        geographical_name = self.get_geographical_name(secondary_feature)
        points = (
            alt.Chart(self.data)
            .transform_aggregate(
                latitude=f"mean({y_attr_abv})",
                longitude=f"mean({x_attr_abv})",
                count="count()",
                groupby=[secondary_feature],
            )
            .mark_circle()
            .encode(
                longitude=f"{x_attr_abv}:Q",
                latitude=f"{y_attr_abv}:Q",
                size=alt.Size("count:Q", title="Number of Records"),
                color=alt.value("steelblue"),
                tooltip=[f"{secondary_feature}:N", "count:Q"],
            )
            .properties(title=f"Number of Records across {geographical_name}")
        )
        chart = background + points
        # Setting tooltip as non-null
        # chart = chart.configure_mark(tooltip=alt.TooltipContent("encoding"))

        ######################################
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

    def get_secondary_feature(self):
        """Returns secondary feature for aggregating lat/long coordinates."""
        assert len(self.vis.intent) == 3
        feature = self.vis.intent[2].get_attr()
        return feature

    def get_background(self, feature):
        """Returns background projection based on secondary feature."""
        from vega_datasets import data

        maps = {
            "state": (alt.topo_feature(data.us_10m.url, feature="states"), "albersUsa"),
            "country": (alt.topo_feature(data.world_110m.url, feature="countries"), "equirectangular"),
        }
        assert feature in maps
        height = 175
        return (
            alt.Chart(maps[feature][0])
            .mark_geoshape(fill="lightgray", stroke="white")
            .properties(width=int(height * (5 / 3)), height=height)
            .project(maps[feature][1])
        )

    def get_geographical_name(self, feature):
        """Returns geographical location label based on secondary feature."""
        maps = {"state": "United States", "country": "World"}
        return maps[feature]

    def encode_color(self):
        # Setting tooltip as non-null
        self.chart = self.chart.configure_mark(tooltip=alt.TooltipContent("encoding"))
        self.code += f"""chart = chart.configure_mark(tooltip=alt.TooltipContent('encoding'))"""
