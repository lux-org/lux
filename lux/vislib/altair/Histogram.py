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


class Histogram(AltairChart):
    """
    Histogram is a subclass of AltairChart that render as a histograms.
    All rendering properties for histograms are set here.

    See Also
    --------
    altair-viz.github.io
    """

    def __init__(self, vis):
        super().__init__(vis)

    def __repr__(self):
        return f"Histogram <{str(self.vis)}>"

    def initialize_chart(self):
        self.tooltip = False
        measure = self.vis.get_attr_by_data_model("measure", exclude_record=True)[0]
        msr_attr = self.vis.get_attr_by_channel(measure.channel)[0]
        msr_attr_abv = str(msr_attr.attribute)

        if len(msr_attr_abv) > 17:
            msr_attr_abv = msr_attr_abv[:10] + "..." + msr_attr_abv[-7:]

        x_min, x_max = self.vis.min_max[msr_attr.attribute]
        x_range = abs(x_max - x_min)

        if isinstance(msr_attr.attribute, str):
            msr_attr.attribute = msr_attr.attribute.replace(".", "")
        markbar = compute_bin_width(self.data[msr_attr.attribute])
        step = abs(self.data[msr_attr.attribute][1] - self.data[msr_attr.attribute][0])

        # Default when bin too small
        if markbar < (x_range / 24):
            markbar = x_max - x_min / 12

        self.data = AltairChart.sanitize_dataframe(self.data)
        end_attr_abv = str(msr_attr.attribute) + "_end"
        self.data[end_attr_abv] = self.data[str(msr_attr.attribute)] + markbar

        axis_title = f"{msr_attr_abv} (binned)"
        if msr_attr.attribute == " ":
            axis_title = "Series (binned)"
        if measure.channel == "x":
            chart = (
                alt.Chart(self.data)
                .mark_bar()
                .encode(
                    x=alt.X(
                        str(msr_attr.attribute),
                        title=axis_title,
                        bin=alt.Bin(binned=True, step=step),
                        type=msr_attr.data_type,
                        axis=alt.Axis(title=axis_title),
                        scale=alt.Scale(domain=[x_min, x_max]),
                    ),
                    x2=end_attr_abv,
                    y=alt.Y("Number of Records", type="quantitative"),
                )
            )
        elif measure.channel == "y":
            chart = (
                alt.Chart(self.data)
                .mark_bar()
                .encode(
                    x=alt.X("Number of Records", type="quantitative"),
                    y=alt.Y(
                        str(msr_attr.attribute),
                        title=axis_title,
                        bin=alt.Bin(binned=True, step=step),
                        type=msr_attr.data_type,
                        axis=alt.Axis(title=axis_title),
                    ),
                    y2=end_attr_abv,
                )
            )
        #####################################
        ## Constructing Altair Code String ##
        #####################################

        self.code += "import altair as alt\n"
        self.code += f"visData = pd.DataFrame({str(self.data.to_dict())})\n"
        if measure.channel == "x":
            self.code += f"""
		chart = alt.Chart(visData).mark_bar().encode(
		    x=alt.X('{msr_attr.attribute}', title='{axis_title}',bin=alt.Bin(binned=True, step={step}), type='{msr_attr.data_type}', axis=alt.Axis(labelOverlap=True, title='{axis_title}'), scale=alt.Scale(domain=({x_min}, {x_max}))),
            x2='{end_attr_abv}',
		    y=alt.Y("Number of Records", type="quantitative")
		)
		"""
        elif measure.channel == "y":
            self.code += f"""
		chart = alt.Chart(visData).mark_bar().encode(
		    y=alt.Y('{msr_attr.attribute}', title='{axis_title}', bin=alt.Bin(binned=True, step={step}), type='{msr_attr.data_type}', axis=alt.Axis(labelOverlap=True, title='{axis_title}')),
            y2='{end_attr_abv}',
		    x=alt.X("Number of Records", type="quantitative")
		)
		"""
        return chart


def compute_bin_width(series):
    """
    Helper function that returns optimal bin size via Freedman Diaconis's Rule
    Source: https://en.wikipedia.org/wiki/Freedman%E2%80%93Diaconis_rule
    """
    import math
    import numpy as np

    data = np.asarray(series)
    num_pts = data.size
    IQR = np.subtract(*np.percentile(data, [75, 25]))
    size = 2 * IQR * (num_pts ** -1 / 3)
    return round(size * 3.5, 2)
