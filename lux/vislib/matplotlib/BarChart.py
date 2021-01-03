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
from lux.utils.utils import get_agg_title
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class BarChart(MatplotlibChart):
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

        x_attr_abv = x_attr.attribute
        y_attr_abv = y_attr.attribute

        if len(x_attr.attribute) > 25:
            x_attr_abv = x_attr.attribute[:15] + "..." + x_attr.attribute[-10:]
        if len(y_attr.attribute) > 25:
            y_attr_abv = y_attr.attribute[:15] + "..." + y_attr.attribute[-10:]

        # x_attr.attribute = x_attr.attribute.replace(".", "")
        # y_attr.attribute = y_attr.attribute.replace(".", "")

        if x_attr.data_model == "measure":
            agg_title = get_agg_title(x_attr)
            measure_attr = x_attr.attribute
            bar_attr = y_attr.attribute
        else:
            agg_title = get_agg_title(y_attr)
            measure_attr = y_attr.attribute
            bar_attr = x_attr.attribute

        df = pd.DataFrame(self.data)

        objects = df[bar_attr]
        y_pos = np.arange(len(objects))
        performance = df[measure_attr]

        fig, ax = plt.subplots()
        ax.bar(y_pos, performance, align='center', alpha=0.5)
        ax.set_xlabel(x_attr_abv)
        ax.set_ylabel(y_attr_abv)

        # Convert chart to HTML
        import base64
        from io import BytesIO
        tmpfile = BytesIO()
        fig.savefig(tmpfile, format='png')
        chart_code = base64.b64encode(tmpfile.getvalue()).decode('utf-8') 
        # Inside chartGallery.tsx change VegaLite component to be adaptable to different rendering mechanism (e.g, img)
        # '<img src=\'data:image/png;base64,{}\'>

        self.code += "import matplotlib.pyplot as plt\n"
        self.code += "import numpy as np\n"

        self.code += f"df = pd.DataFrame({str(self.data.to_dict())})\n"

        self.code += f"fig, ax = plt.subplots()\n"
        self.code += f"objects = df['{bar_attr}']\n"
        self.code += f"y_pos = np.arrange(len(objects))\n"
        self.code += f"performance = df['{measure_attr}']\n"

        self.code += f"ax.bar(y_pos, performance, align='center', alpha=0.5)\n"
        self.code += f"ax.set_xlabel('{x_attr_abv}')\n"
        self.code += f"ax.set_ylabel('{y_attr_abv}')\n"
        return chart_code
