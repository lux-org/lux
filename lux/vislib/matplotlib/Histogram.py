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

from lux.vislib.matplotlib.MatplotlibChart import MatplotlibChart
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class Histogram(MatplotlibChart):
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

        msr_attr_abv = msr_attr.attribute

        if len(msr_attr.attribute) > 17:
            msr_attr_abv = msr_attr.attribute[:10] + "..." + msr_attr.attribute[-7:]

        x_min = self.vis.min_max[msr_attr.attribute][0]
        x_max = self.vis.min_max[msr_attr.attribute][1]

        # msr_attr.attribute = msr_attr.attribute.replace(".", "")

        x_range = abs(max(self.vis.data[msr_attr.attribute]) - min(self.vis.data[msr_attr.attribute]))
        plot_range = abs(x_max - x_min)
        markbar = x_range / plot_range * 12

        df = pd.DataFrame(self.data)

        objects = df[msr_attr.attribute]
        
        fig, ax = plt.subplots()
        counts, bins = np.histogram(self.data)
        ax.hist(bins[:-1], bins, weights=counts, range=(x_min, x_max))



        if measure.channel == "x":
            ax.set_xlabel(f"{msr_attr.attribute} (binned)")
            ax.set_ylabel("Number of Records")
        elif measure.channel == "y":
            ax.set_xlabel("Number of Records")
            ax.set_ylabel(f"{msr_attr.attribute} (binned)")
        # Convert chart to HTML
        import base64
        from io import BytesIO
        tmpfile = BytesIO()
        fig.savefig(tmpfile, format='png')
        chart_code = base64.b64encode(tmpfile.getvalue()).decode('utf-8') 
        # Inside chartGallery.tsx change VegaLite component to be adaptable to different rendering mechanism (e.g, img)
        # '<img src=\'data:image/png;base64,{}\'>
        return chart_code