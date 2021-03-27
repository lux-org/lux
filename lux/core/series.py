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
from typing import Dict, Union, List, Callable


class LuxSeries(pd.Series):
    """
    A subclass of pd.Series that supports all 1-D Series operations
    """

    _metadata = [
        "_intent",
        "_inferred_intent",
        "_data_type",
        "unique_values",
        "cardinality",
        "_rec_info",
        "_min_max",
        "plotting_style",
        "_current_vis",
        "_widget",
        "_recommendation",
        "_prev",
        "_history",
        "_saved_export",
        "name",
        "_sampled",
        "_toggle_pandas_display",
        "_message",
        "_pandas_only",
        "pre_aggregated",
        "_type_override",
    ]

    _default_metadata = {
        "_intent": list,
        "_inferred_intent": list,
        "_current_vis": list,
        "_recommendation": list,
        "_toggle_pandas_display": lambda: True,
        "_pandas_only": lambda: False,
        "_type_override": dict,
        "_history": History,
        "_message": Message,
    }

    def __init__(self, *args, **kw):
        super(LuxSeries, self).__init__(*args, **kw)
        for attr in self._metadata:
            if attr in self._default_metadata:
                self.__dict__[attr] = self._default_metadata[attr]()
            else:
                self.__dict__[attr] = None

    @property
    def _constructor(self):
        return LuxSeries

    @property
    def _constructor_expanddim(self):
        from lux.core.frame import LuxDataFrame

        def f(*args, **kwargs):
            df = LuxDataFrame(*args, **kwargs)
            for attr in self._metadata:
                # if attr in self._default_metadata:
                #     default = self._default_metadata[attr]
                # else:
                #     default = None
                df.__dict__[attr] = getattr(self, attr, None)
            return df

        f._get_axis_number = LuxDataFrame._get_axis_number
        return f

    def to_pandas(self) -> pd.Series:
        """
        Convert Lux Series to Pandas Series

        Returns
        -------
        pd.Series
        """
        import lux.core

        return lux.core.originalSeries(self, copy=False)

    def _ipython_display_(self):
        from IPython.display import display
        from IPython.display import clear_output
        import ipywidgets as widgets
        from lux.core.frame import LuxDataFrame

        series_repr = super(LuxSeries, self).__repr__()

        ldf = LuxDataFrame(self)

        # Default column name 0 causes errors
        if self.name is None:
            ldf = ldf.rename(columns={0: " "})
        self._ldf = ldf

        try:
            # Ignore recommendations when Series a results of:
            # 1) Values of the series are of dtype objects (df.dtypes)
            is_dtype_series = (
                all(isinstance(val, np.dtype) for val in self.values) and len(self.values) != 0
            )
            # 2) Mixed type, often a result of a "row" acting as a series (df.iterrows, df.iloc[0])
            # Tolerant for NaNs + 1 type
            mixed_dtype = len(set([type(val) for val in self.values])) > 2
            if ldf._pandas_only or is_dtype_series or mixed_dtype:
                print(series_repr)
                ldf._pandas_only = False
            else:
                if not self.index.nlevels >= 2:
                    ldf.maintain_metadata()

                if lux.config.default_display == "lux":
                    self._toggle_pandas_display = False
                else:
                    self._toggle_pandas_display = True

                # df_to_display.maintain_recs() # compute the recommendations (TODO: This can be rendered in another thread in the background to populate self._widget)
                ldf.maintain_recs(is_series="Series")

                # Observers(callback_function, listen_to_this_variable)
                ldf._widget.observe(ldf.remove_deleted_recs, names="deletedIndices")
                ldf._widget.observe(ldf.set_intent_on_click, names="selectedIntentIndex")

                self._widget = ldf._widget
                self._recommendation = ldf._recommendation

                # box = widgets.Box(layout=widgets.Layout(display='inline'))
                button = widgets.Button(
                    description="Toggle Pandas/Lux",
                    layout=widgets.Layout(width="140px", top="5px"),
                )
                ldf.output = widgets.Output()
                # box.children = [button,output]
                # output.children = [button]
                # display(box)
                display(button, ldf.output)

                def on_button_clicked(b):
                    with ldf.output:
                        if b:
                            self._toggle_pandas_display = not self._toggle_pandas_display
                        clear_output()
                        if self._toggle_pandas_display:
                            print(series_repr)
                        else:
                            # b.layout.display = "none"
                            display(ldf._widget)
                            # b.layout.display = "inline-block"

                button.on_click(on_button_clicked)
                on_button_clicked(None)

        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            warnings.warn(
                "\nUnexpected error in rendering Lux widget and recommendations. "
                "Falling back to Pandas display.\n"
                "Please report the following issue on Github: https://github.com/lux-org/lux/issues \n",
                stacklevel=2,
            )
            warnings.warn(traceback.format_exc())
            display(self.to_pandas())

    @property
    def recommendation(self):
        from lux.core.frame import LuxDataFrame

        if self._recommendation is not None and self._recommendation == {}:
            if self.name is None:
                self.name = " "
            ldf = LuxDataFrame(self)

            ldf.maintain_metadata()
            ldf.maintain_recs()
            self._recommendation = ldf._recommendation
        return self._recommendation

    @property
    def exported(self) -> Union[Dict[str, VisList], VisList]:
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
        Union[Dict[str,VisList], VisList]
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
