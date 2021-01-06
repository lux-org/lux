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

class ScatterChart(MatplotlibChart):
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

        x_attr_abv = x_attr.attribute
        y_attr_abv = y_attr.attribute

        if len(x_attr.attribute) > 25:
            x_attr_abv = x_attr.attribute[:15] + "..." + x_attr.attribute[-10:]
        if len(y_attr.attribute) > 25:
            y_attr_abv = y_attr.attribute[:15] + "..." + y_attr.attribute[-10:]

        x_min = self.vis.min_max[x_attr.attribute][0]
        x_max = self.vis.min_max[x_attr.attribute][1]

        y_min = self.vis.min_max[y_attr.attribute][0]
        y_max = self.vis.min_max[y_attr.attribute][1]

        # x_attr.attribute = x_attr.attribute.replace(".", "")
        # y_attr.attribute = y_attr.attribute.replace(".", "")

        df = pd.DataFrame(self.data)

        objects = df[x_attr.attribute]
        y_pos = np.arange(len(objects))
        performance = df[y_attr.attribute]

        fig, ax = plt.subplots(figsize=(5,4))
        ax.scatter(objects, performance)
        ax.set_xlabel(x_attr_abv)
        ax.set_ylabel(y_attr_abv)
        plt.tight_layout()

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
        self.code += f"objects = df['{x_attr.attribute}']\n"
        self.code += f"y_pos = np.arrange(len(objects))\n"
        self.code += f"performance = df['{y_attr.attribute}']\n"

        self.code += f"ax.scatter(objects, performance)\n"
        self.code += f"ax.set_xlabel('{x_attr_abv}')\n"
        self.code += f"ax.set_ylabel('{y_attr_abv}')\n"
        return chart_code
