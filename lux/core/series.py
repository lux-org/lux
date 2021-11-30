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

import pandas as pd
import lux
import warnings
import traceback
import numpy as np
from lux.history.history import History
from lux.utils.message import Message
from lux.vis.VisList import VisList
from lux.core.lux_methods import LuxMethods
import typing as tp


class LuxSeries(pd.Series):
    _metadata: tp.List[str]
    _LUX_: "LuxSeriesMethods"

    @property
    def lux(self) -> "LuxSeriesMethods":
        ...


class LuxSeriesMethods(LuxMethods):
    series: pd.Series

    def __init__(self, series: pd.Series):
        self.series = series

        # with default
        self._intent = []
        self._inferred_intent = []
        self._current_vis = []
        self._recommendation = []
        self._toggle_pandas_display = True
        self._pandas_only = False
        self._type_override = {}
        self._history = History()
        self._message = Message()
        # rest
        self._data_type = None
        self.unique_values = None
        self.cardinality = None
        self._rec_info = None
        self._min_max = None
        self.plotting_style = None
        self._widget = None
        self._prev = None
        self._saved_export = None
        self.name = None
        self._sampled = None
        self.pre_aggregated = None

    def unique(self):
        """
        Overridden method for pd.Series.unique with cached results.
        Return unique values of Series object.
        Uniques are returned in order of appearance. Hash table-based unique,
        therefore does NOT sort.
        Returns
        -------
        ndarray or ExtensionArray
            The unique values returned as a NumPy array.
        See Also
        --------
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.unique.html
        """
        if self.unique_values and self.name in self.unique_values.keys():
            return np.array(self.unique_values[self.name])
        else:
            return self.series.unique()

    @property
    def recommendation(self):
        from lux.core.frame import LuxDataFrame

        if self._recommendation is not None and self._recommendation == {}:
            if self.name is None:
                self.name = " "
            ldf = LuxDataFrame(self)

            ldf.maintain_metadata()
            ldf.maintain_recs()
            self._recommendation = ldf.lux._recommendation
        return self._recommendation

    @property
    def exported(self) -> tp.Union[tp.Dict[str, VisList], VisList]:
        """
        Get selected visualizations as exported Vis List

        Notes
        -----
        Convert the _selectedVisIdxs dictionary into a programmable VisList
        Example _selectedVisIdxs :

            {'Correlation': [0, 2], 'Occurrence': [1]}

        indicating the 0th and 2nd vis from the `Correlation` tab is selected, and the 1st vis from the `Occurrence` tab is selected.

        Returns
        -------
        tp.Union[tp.Dict[str,VisList], VisList]
                When there are no exported vis, return empty list -> []
                When all the exported vis is from the same tab, return a VisList of selected visualizations. -> VisList(v1, v2...)
                When the exported vis is from the different tabs, return a dictionary with the action name as key and selected visualizations in the VisList. -> {"Enhance": VisList(v1, v2...), "Filter": VisList(v5, v7...), ..}
        """
        return self._ldf.exported

    def groupby(self, *args, **kwargs):
        history_flag = False
        if "history" not in kwargs or ("history" in kwargs and kwargs["history"]):
            history_flag = True
        if "history" in kwargs:
            del kwargs["history"]
        groupby_obj = super(LuxSeries, self).groupby(*args, **kwargs)
        for attr in self._metadata:
            groupby_obj.__dict__[attr] = getattr(self, attr, None)
        if history_flag:
            groupby_obj._history = groupby_obj._history.copy()
            groupby_obj._history.append_event("groupby", *args, **kwargs)
        groupby_obj.pre_aggregated = True
        return groupby_obj
