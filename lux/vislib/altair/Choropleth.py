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
import pandas as pd
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
        # Override default width and height
        self.width = 200

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
            .properties(title=f"Mean of {y_attr_abv} across {geographical_name}")
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
        background = (
            alt.Chart(maps[feature][0])
            .mark_geoshape(fill="lightgray", stroke="white")
            .project(maps[feature][1])
        )
        background_str = f"(alt.Chart({maps[feature][2]}).mark_geoshape(fill='lightgray', stroke='white').project('{maps[feature][1]}'))"
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
        usa = pd.DataFrame(
            [
                {"fips": 1, "state": "alabama", "abbrev": "al"},
                {"fips": 2, "state": "alaska", "abbrev": "ak"},
                {"fips": 4, "state": "arizona", "abbrev": "az"},
                {"fips": 5, "state": "arkansas", "abbrev": "ar"},
                {"fips": 6, "state": "california", "abbrev": "ca"},
                {"fips": 8, "state": "colorado", "abbrev": "co"},
                {"fips": 9, "state": "connecticut", "abbrev": "ct"},
                {"fips": 10, "state": "delaware", "abbrev": "de"},
                {"fips": 11, "state": "district of columbia", "abbrev": "dc"},
                {"fips": 12, "state": "florida", "abbrev": "fl"},
                {"fips": 13, "state": "georgia", "abbrev": "ga"},
                {"fips": 15, "state": "hawaii", "abbrev": "hi"},
                {"fips": 16, "state": "idaho", "abbrev": "id"},
                {"fips": 17, "state": "illinois", "abbrev": "il"},
                {"fips": 18, "state": "indiana", "abbrev": "in"},
                {"fips": 19, "state": "iowa", "abbrev": "ia"},
                {"fips": 20, "state": "kansas", "abbrev": "ks"},
                {"fips": 21, "state": "kentucky", "abbrev": "ky"},
                {"fips": 22, "state": "louisiana", "abbrev": "la"},
                {"fips": 23, "state": "maine", "abbrev": "me"},
                {"fips": 24, "state": "maryland", "abbrev": "md"},
                {"fips": 25, "state": "massachusetts", "abbrev": "ma"},
                {"fips": 26, "state": "michigan", "abbrev": "mi"},
                {"fips": 27, "state": "minnesota", "abbrev": "mn"},
                {"fips": 28, "state": "mississippi", "abbrev": "ms"},
                {"fips": 29, "state": "missouri", "abbrev": "mo"},
                {"fips": 30, "state": "montana", "abbrev": "mt"},
                {"fips": 31, "state": "nebraska", "abbrev": "ne"},
                {"fips": 32, "state": "nevada", "abbrev": "nv"},
                {"fips": 33, "state": "new hampshire", "abbrev": "nh"},
                {"fips": 34, "state": "new jersey", "abbrev": "nj"},
                {"fips": 35, "state": "new mexico", "abbrev": "nm"},
                {"fips": 36, "state": "new york", "abbrev": "ny"},
                {"fips": 37, "state": "north carolina", "abbrev": "nc"},
                {"fips": 38, "state": "north dakota", "abbrev": "nd"},
                {"fips": 39, "state": "ohio", "abbrev": "oh"},
                {"fips": 40, "state": "oklahoma", "abbrev": "ok"},
                {"fips": 41, "state": "oregon", "abbrev": "or"},
                {"fips": 42, "state": "pennsylvania", "abbrev": "pa"},
                {"fips": 44, "state": "rhode island", "abbrev": "ri"},
                {"fips": 45, "state": "south carolina", "abbrev": "sc"},
                {"fips": 46, "state": "south dakota", "abbrev": "sd"},
                {"fips": 47, "state": "tennessee", "abbrev": "tn"},
                {"fips": 48, "state": "texas", "abbrev": "tx"},
                {"fips": 49, "state": "utah", "abbrev": "ut"},
                {"fips": 50, "state": "vermont", "abbrev": "vt"},
                {"fips": 51, "state": "virginia", "abbrev": "va"},
                {"fips": 53, "state": "washington", "abbrev": "wa"},
                {"fips": 54, "state": "west virginia", "abbrev": "wv"},
                {"fips": 55, "state": "wisconsin", "abbrev": "wi"},
                {"fips": 56, "state": "wyoming", "abbrev": "wy"},
            ]
        )
        attribute = attribute.lower()
        match = usa[(usa.state == attribute) | (usa.abbrev == attribute)]
        if len(match) == 1:
            return match["fips"].values[0]
        else:
            if attribute in ["washington d.c.", "washington dc", "d.c.", "d.c"]:
                return 11
            else:
                return 0  # any unmatching value (e.g. nan)

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
