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
import us
from iso3166 import countries

alt.data_transformers.disable_max_rows()


class Choropleth(AltairChart):
    """
    Choropleth is a subclass of AltairChart that renders choropleth maps.
    All rendering properties for proportional symbol maps are set here.

    See Also
    --------
    altair-viz.github.io
    """

    us_url = "https://cdn.jsdelivr.net/npm/vega-datasets@v1.29.0/data/us-10m.json"
    world_url = "https://cdn.jsdelivr.net/npm/vega-datasets@v1.29.0/data/world-110m.json"

    def __init__(self, dobj):
        super().__init__(dobj)

    def __repr__(self):
        return f"Choropleth Map <{str(self.vis)}>"

    def initialize_chart(self):
        x_attr = self.vis.get_attr_by_channel("x")[0]
        y_attr = self.vis.get_attr_by_channel("y")[0]

        x_attr_abv = str(x_attr.attribute)
        y_attr_abv = str(y_attr.attribute)

        background, background_str = self.get_background(x_attr_abv.lower())
        geographical_name = self.get_geographical_name(x_attr_abv.lower())
        geo_map, geo_map_str, map_type, map_translation = self.get_geomap(x_attr_abv.lower())
        self.data[x_attr_abv] = self.data[x_attr_abv].apply(map_translation)

        if len(x_attr_abv) > 25:
            x_attr_abv = x_attr.attribute[:15] + "..." + x_attr.attribute[-10:]
        if len(y_attr_abv) > 25:
            y_attr_abv = y_attr.attribute[:15] + "..." + y_attr.attribute[-10:]

        if isinstance(x_attr.attribute, str):
            x_attr.attribute = x_attr.attribute.replace(".", "")
        if isinstance(y_attr.attribute, str):
            y_attr.attribute = y_attr.attribute.replace(".", "")

        self.data = AltairChart.sanitize_dataframe(self.data)
        height = 175
        width = int(height * (5 / 3))

        points = (
            alt.Chart(geo_map)
            .mark_geoshape()
            .encode(
                color=f"{str(y_attr.attribute)}:Q",
            )
            .transform_lookup(
                lookup="id",
                from_=alt.LookupData(self.data, str(x_attr.attribute), [str(y_attr.attribute)]),
            )
            .project(type=map_type)
            .properties(
                width=width, height=height, title=f"Mean of {y_attr_abv} across {geographical_name}"
            )
        )

        chart = background + points

        ######################################
        ## Constructing Altair Code String ##
        #####################################

        self.code += "import altair as alt\n"
        dfname = "placeholder_variable"
        self.code += f"""nan=float('nan')
df = pd.DataFrame({str(self.data.to_dict())})
background = {background_str}

		points = alt.Chart({geo_map_str}).mark_geoshape().encode(
    color='{str(y_attr.attribute)}:Q',
).transform_lookup(
    lookup='id',
    from_=alt.LookupData({dfname}, "{str(x_attr.attribute)}", ["{str(y_attr.attribute)}"])
).project(
    type="{map_type}"
).properties(
    width={width},
    height={height},
    title="Mean of {y_attr_abv} across {geographical_name}"
)
chart = background + points
		"""
        return chart

    def get_background(self, feature):
        """Returns background projection based on geographic feature."""
        maps = {
            "state": (
                alt.topo_feature(Choropleth.us_url, feature="states"),
                "albersUsa",
                f"alt.topo_feature('{Choropleth.us_url}', feature='states')",
            ),
            "country": (
                alt.topo_feature(Choropleth.world_url, feature="countries"),
                "equirectangular",
                f"alt.topo_feature('{Choropleth.world_url}', feature='countries')",
            ),
        }
        assert feature in maps
        height = 175
        background = (
            alt.Chart(maps[feature][0])
            .mark_geoshape(fill="lightgray", stroke="white")
            .properties(width=int(height * (5 / 3)), height=height)
            .project(maps[feature][1])
        )
        background_str = f"(alt.Chart({maps[feature][2]}).mark_geoshape(fill='lightgray', stroke='white').properties(width=int({height} * (5 / 3)), height={height}).project('{maps[feature][1]}'))"
        return background, background_str

    def get_geomap(self, feature):
        """Returns topological encoding, topological style,
        and translation function based on geographic feature"""
        maps = {
            "state": (
                alt.topo_feature(Choropleth.us_url, feature="states"),
                f"alt.topo_feature('{Choropleth.us_url}', feature='states')",
                "albersUsa",
                self.get_us_fips_code,
            ),
            "country": (
                alt.topo_feature(Choropleth.world_url, feature="countries"),
                f"alt.topo_feature('{Choropleth.world_url}', feature='countries')",
                "equirectangular",
                self.get_country_iso_code,
            ),
        }
        assert feature in maps
        return maps[feature]

    def get_us_fips_code(self, attribute):
        """Returns FIPS code given a US state"""
        if not isinstance(attribute, str):
            return attribute
        try:
            return int(us.states.lookup(attribute).fips)
        except:
            return attribute

    def get_country_iso_code(self, attribute):
        """Returns country ISO code given a country"""
        if not isinstance(attribute, str):
            return attribute
        try:
            return int(countries.get(attribute).numeric)
        except:
            return attribute

    def get_geographical_name(self, feature):
        """Returns geographical location label based on secondary feature."""
        maps = {"state": "United States", "country": "World"}
        return maps[feature]

    def encode_color(self):
        # Setting tooltip as non-null
        self.chart = self.chart.configure_mark(tooltip=alt.TooltipContent("encoding"))
        self.code += f"""chart = chart.configure_mark(tooltip=alt.TooltipContent('encoding'))"""
