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

        self.data = AltairChart.sanitize_dataframe(self.data)

        chart = alt.Chart(self.data).mark_boxplot(
            outliers=alt.MarkConfig(filled=True)
            ).encode(
            x=alt.X(f'{y_attr_abv}:Q', sort=self.data._order.get(y_attr_abv, [])),
            y=alt.Y(f'{x_attr_abv}:O')
        )
        
        #####################################
        ## Constructing Altair Code String ##
        #####################################
        
        self.code += "import altair as alt\n"
        dfname = "placeholder_variable"
        self.code += f"""chart = alt.Chart({dfname}).mark_boxplot().encode(
            x={x_attr_abv}:O,
            y={y_attr_abv}:Q
            """
        
        return chart