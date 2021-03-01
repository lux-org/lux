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

from typing import List, Callable, Union
from lux.vis.Clause import Clause
from lux.utils.utils import check_import_lux_widget
import lux
import warnings
from IPython.core.debugger import set_trace


class CustomVis:
    """
    Vis Object represents a collection of fully fleshed out specifications required for data fetching and visualization.
    """

    def __init__(self, altChart):
        self._code = altChart
        self.score = 1
        
    def _repr_html_(self):
        set_trace()

        from IPython.display import display

        check_import_lux_widget()
        import luxwidget

        from lux.core.frame import LuxDataFrame

        widget = luxwidget.LuxWidget(
            currentVis= self.to_code(),
            recommendations=[],
            intent="",
            message="",
        )
        display(widget)


    def to_code(self, language="vegalite", **kwargs):
        """
        Export Vis object to code specification

        Parameters
        ----------
        language : str, optional
            choice of target language to produce the visualization code in, by default "vegalite"

        Returns
        -------
        spec:
            visualization specification corresponding to the Vis object
        """
        chart_dict = self._code.to_dict()
        chart_dict["vislib"] = "vegalite"
        return chart_dict


