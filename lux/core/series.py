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

from pandas._typing import (
    FrameOrSeries,
    ArrayLike,
)
from typing import (
    Optional,
    Tuple,
    Union,
    Hashable,
)

from IPython.core.debugger import set_trace


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
        # for attr in self._metadata:
        #     if attr in self._default_metadata:
        #         self.__dict__[attr] = self._default_metadata[attr]()
        #     else:
        #         self.__dict__[attr] = None
        
        # defaults
        self._intent = []
        self._inferred_intent = []
        self._current_vis = []
        self._recommendation = []
        self._toggle_pandas_display = True
        self._pandas_only = False
        self._type_override = {}
        self._history = History(self)
        self._message = Message()

        # others 
        self._data_type  = None
        self.unique_values  = None 
        self.cardinality  = None 
        self._rec_info  = None 
        self._min_max  = None 
        self.plotting_style  = None 
        self._widget  = None 
        self._prev  = None 
        self._saved_export  = None 
        self._sampled  = None 
        self.pre_aggregated  = None  
        self._parent_df = None # if series comes from a df this will be populated with ref to df

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
    
    @property
    def history(self):
        return self._history

    def to_pandas(self) -> pd.Series:
        """
        Convert Lux Series to Pandas Series

        Returns
        -------
        pd.Series
        """
        import lux.core

        return lux.core.originalSeries(self, copy=False)

    def __repr__(self):
        from IPython.display import display
        from IPython.display import clear_output
        import ipywidgets as widgets
        from lux.core.frame import LuxDataFrame

        series_repr = super(LuxSeries, self).__repr__()
        # Default column name 0 causes errors
        if self.name is None:
            self.name = " "
        
        # set_trace()
        ldf = LuxDataFrame(self)

        try:
            # Ignore recommendations when Series a results of:
            # 1) Values of the series are of dtype objects (df.dtypes)
            is_dtype_series = all(isinstance(val, np.dtype) for val in self.values)
            # 2) Mixed type, often a result of a "row" acting as a series (df.iterrows, df.iloc[0])
            # Tolerant for NaNs + 1 type
            mixed_dtype = len(set([type(val) for val in self.values])) > 2
            if ldf._pandas_only or is_dtype_series or mixed_dtype:
                print(series_repr)
                ldf._pandas_only = False
            else:
                if self.index.nlevels >= 2:
                    warnings.warn(
                        "\nLux does not currently support series "
                        "with hierarchical indexes.\n"
                        "Please convert the series into a flat "
                        "table via `pandas.DataFrame.reset_index`.\n",
                        stacklevel=2,
                    )
                    print(series_repr)
                    return ""

                if len(self) <= 0:
                    warnings.warn(
                        "\nLux can not operate on an empty series.\nPlease check your input again.\n",
                        stacklevel=2,
                    )
                    print(series_repr)
                    return ""
                ldf.maintain_metadata()

                if lux.config.default_display == "lux":
                    self._toggle_pandas_display = False
                else:
                    self._toggle_pandas_display = True

                # df_to_display.maintain_recs() # compute the recommendations (TODO: This can be rendered in another thread in the background to populate self._widget)
                ldf.maintain_recs()

                # Observers(callback_function, listen_to_this_variable)
                ldf._widget.observe(ldf.remove_deleted_recs, names="deletedIndices")
                ldf._widget.observe(ldf.set_intent_on_click, names="selectedIntentIndex")

                if len(ldf.recommendation) > 0:
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
                else:
                    warnings.warn(
                        "\nLux defaults to Pandas when there are no valid actions defined.",
                        stacklevel=2,
                    )
                    print(series_repr)

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
        return ""

    @property
    def recommendation(self):
        from lux.core.frame import LuxDataFrame

        if self.name is None:
            self.name = " "
        ldf = LuxDataFrame(self)

        if self._recommendation is not None and self._recommendation == {}:
            ldf.maintain_metadata()
            ldf.maintain_recs()
        return ldf._recommendation
    
    #####################
    ## Override Pandas ##
    #####################
    def __finalize__(
        self: FrameOrSeries, other, method: Optional[str] = None, **kwargs
    ) -> FrameOrSeries:
        """
        See same method in frame.py
        """
        _this = super(LuxSeries, self).__finalize__(other, method, **kwargs)
        _this._history = _this._history.copy()
        return _this

    # def _construct_result(
    #     self, result: Union[ArrayLike, Tuple[ArrayLike, ArrayLike]], name: Hashable
    # ) -> Union[pd.Series, Tuple[pd.Series, pd.Series]]:
    #     ret_value = super(LuxSeries, self)._construct_result(result, name)

    #     set_trace()

    #     print(type(ret_value))

    #     return ret_value
    
    def value_counts(
        self,
        normalize: bool = False,
        sort: bool = True,
        ascending: bool = False,
        bins=None,
        dropna: bool = True,
    ):
        ret_value = super(LuxSeries, self).value_counts(normalize, sort, ascending, bins, dropna)
        ret_value._parent_df = self._parent_df # propagate parent from column to vc series
        # add to history
        kw = {"normalize":normalize, 
                "sort":sort, 
                "ascending":ascending, 
                "bins":bins, 
                "dropna":dropna}

        self._history.append_event("value_counts", [self.name], **kw)
        ret_value._history.append_event("value_counts", [self.name], **kw)
        self.add_to_parent_history("value_counts", [self.name], **kw)
        
        return ret_value
    
    def unique(self):
        """
        Returns a numpy array so makes things more tricky
        """
        #set_trace()
        ret_value = super(LuxSeries, self).unique()
        self._history.append_event("unique", [self.name])
        #ret_value._history.append_event("unique", [self.name])
        self.add_to_parent_history("unique", [self.name])

        return ret_value
    
    
    #################
    # History Utils #
    #################
    
    def add_to_parent_history(self, op, cols, **kw_dict):
        """
        Utility function for updating parent history

        N.B.: for df.col.value_counts() this is actually adding to the parent of df.col, 
        not df.col.value_counts() so works how we want but is a subtle distinction.
        """
        if self._parent_df is not None:
            if self._parent_df.history.check_event(-1, op_name="col_ref", cols=cols):
                self._parent_df.history.edit_event(-1, op, cols, **kw_dict)
            else: 
                self._parent_df._history.append_event(op, cols, **kw_dict)
