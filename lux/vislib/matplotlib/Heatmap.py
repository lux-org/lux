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

class Heatmap(MatplotlibChart):
    """
    Heatmap is a subclass of AltairChart that render as a heatmap.
    All rendering properties for heatmap are set here.

    See Also
    --------
    altair-viz.github.io
    """

    def __init__(self, vis):
        super().__init__(vis)

    def __repr__(self):
        return f"Heatmap <{str(self.vis)}>"

    def initialize_chart(self):
        # return NotImplemented
        x_attr = self.vis.get_attr_by_channel("x")[0]
        y_attr = self.vis.get_attr_by_channel("y")[0]

        x_attr_abv = x_attr.attribute
        y_attr_abv = y_attr.attribute

        if len(x_attr.attribute) > 25:
            x_attr_abv = x_attr.attribute[:15] + "..." + x_attr.attribute[-10:]
        if len(y_attr.attribute) > 25:
            y_attr_abv = y_attr.attribute[:15] + "..." + y_attr.attribute[-10:]
        
        import seaborn as sns

        df = pd.pivot_table(data=self.data,
                    index='xBinStart',
                    values='count',
                    columns='yBinStart')
        df = df.apply(lambda x : np.log(x), axis=1)   

        fig, ax = plt.subplots()

        ax = sns.heatmap(
            df,
            cbar=False,
            square=True,
            cmap='Blues',
        )

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
        self.code += "import seaborn as sns\n"

        self.code += f"""df = pd.pivot_table(data={str(self.data.to_dict())},
                    index='xBinStart',
                    values='count',
                    columns='yBinStart')\n
		"""
        self.code += f"df = df.apply(lambda x : np.log(x), axis=1)\n"

        self.code += f"fig, ax = plt.subplots()\n"

        self.code += f"""
        ax = sns.heatmap(df,
            cbar=False,
            square=True,
            cmap='Blues',
        )\n"""
        self.code += f"ax.set_xlabel('{x_attr_abv}')\n"
        self.code += f"ax.set_ylabel('{y_attr_abv}')\n"
        return chart_code

