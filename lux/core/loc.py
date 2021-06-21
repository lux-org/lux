import pandas as pd
from lux.history.history import History
from lux.core.series import LuxSeries
from lux.core.frame import LuxDataFrame
from lux.utils.utils import convert_indices_to_columns, convert_names_to_columns
from typing import Tuple
class LuxLocIndexer(pd.core.indexing._LocIndexer):

    _metadata = [
        "_intent",
        "_inferred_intent",
        "_data_type",
        "unique_values",
        "cardinality",
        "_rec_info",
        "_min_max",
        "_current_vis",
        "_widget",
        "_recommendation",
        "_prev",
        "_history",
        "_parent_df",
        "_saved_export",
        "_sampled",
        "_toggle_pandas_display",
        "_message",
        "_pandas_only",
        "pre_aggregated",
        "_type_override",
    ]

    def __init__(self, *args, **kwargs):
        super(LuxLocIndexer, self).__init__(*args, **kwargs)
        self._history = History(self) 
        self._parent_df = None
    
    @property
    def history(self):
        return self._history
    
    @history.setter
    def history(self, history: History):
        self._history = history

    def __getitem__(self, key):
        if self._parent_df is not None:
            self._parent_df.history.freeze()
            ret_value = super(LuxLocIndexer, self).__getitem__(key)
            self._parent_df.history.unfreeze()
            if not isinstance(ret_value, LuxSeries) and not isinstance(ret_value, LuxDataFrame):
                # then only a single value will be returned. 
                # In this case, we modify the history of the parent dataframe and 
                # note that here the key should be a two-element tuple 
                # and the second element is the column the user is intereseted in
                self._parent_df.history.append_event("loc", [key[1]], rank_type="parent", child_df=ret_value)
        else:
            ret_value = super(LuxLocIndexer, self).__getitem__(key)
        return ret_value

    def _getitem_axis(self, key, axis: int):
        ret_value = super(LuxLocIndexer, self)._getitem_axis(key, axis)
        ret_value = self._lux_copymd(ret_value)
        ret_value._parent_df = self._parent_df
        ret_value.history.append_event("loc", [], rank_type="child", child_df=None)
        return ret_value

    def _getitem_tuple(self, tup: Tuple):
        ret_value = super(LuxLocIndexer, self)._getitem_tuple(tup)
        ret_value = self._lux_copymd(ret_value)
        ret_value._parent_df = self._parent_df
        if self._parent_df is not None:
            # _getitem_tuple will be called inside the inner codes of pandas
            columns = convert_names_to_columns(self._parent_df.columns, tup)
            # inside the _getitem_tuple the function _getitem_axis might be called
            # at least when we call df.loc["cobra", ["shield", "max_speed"]]
            if ret_value.history.check_event(-1, op_name="loc"):
                ret_value.history.edit_event(-1, "loc", columns, rank_type="child", child_df=None)
            else:
                ret_value.history.append_event("loc", columns, rank_type="child", child_df=None)
        return ret_value
    
    def __setitem__(self, key, value):
        if self._parent_df is not None:
            self._parent_df.history.freeze()
            super(LuxLocIndexer, self).__setitem__(key, value)
            self._parent_df.history.unfreeze()
            if isinstance(key, tuple):
                # here some columns must be referenced
                columns = convert_names_to_columns(self._parent_df.columns, key)
                if columns is not None: 
                    # if the key[1] is multi-index instead of list, str, slice, 
                    # we choose to not log such action for now.
                    self._parent_df.history.append_event("loc", columns, rank_type="parent", child_df=None)
            else:
                # only some rows have been referenced
                self._parent_df.history.append_event("loc", [], rank_type="parent", child_df=None)
        else:
            super(LuxLocIndexer, self).__setitem__(key, value)
    
    def _lux_copymd(self, ret_value):
        for attr in self._metadata:
            ret_value.__dict__[attr] = getattr(self, attr, None)
        
        ret_value.history = ret_value.history.copy()
        return ret_value

class iLuxLocIndexer(pd.core.indexing._iLocIndexer):

    _metadata = [
        "_intent",
        "_inferred_intent",
        "_data_type",
        "unique_values",
        "cardinality",
        "_rec_info",
        "_min_max",
        "_current_vis",
        "_widget",
        "_recommendation",
        "_prev",
        "_history",
        "_parent_df",
        "_saved_export",
        "_sampled",
        "_toggle_pandas_display",
        "_message",
        "_pandas_only",
        "pre_aggregated",
        "_type_override",
    ]

    def __init__(self, *args, **kwargs):
        super(iLuxLocIndexer, self).__init__(*args, **kwargs)
        self._history = History(self) 
        self._parent_df = None
    
    @property
    def history(self):
        return self._history
    
    @history.setter
    def history(self, history: History):
        self._history = history

    def __getitem__(self, key):
        if self._parent_df is not None:
            self._parent_df.history.freeze()
            ret_value = super(iLuxLocIndexer, self).__getitem__(key)
            self._parent_df.history.unfreeze()
            if not isinstance(ret_value, LuxSeries) and not isinstance(ret_value, LuxDataFrame):
                # then only a single value will be returned. 
                # In this case, we modify the history of the parent dataframe and 
                # note that here the key should be a two-element tuple 
                # and the second element is the column the user is intereseted in
                self._parent_df.history.append_event("iloc", self._parent_df.columns[key[1]], rank_type="parent", child_df=ret_value)
        else:
            ret_value = super(iLuxLocIndexer, self).__getitem__(key)
        return ret_value
    
    def __setitem__(self, key, value):
        if self._parent_df is not None:
            self._parent_df.history.freeze()
            super(iLuxLocIndexer, self).__setitem__(key, value)
            self._parent_df.history.unfreeze()
            if isinstance(key, tuple):
                # here some columns must be referenced
                columns = convert_indices_to_columns(self._parent_df.columns, key)
                if columns is not None: 
                    # if the key[1] is multi-index instead of list, int, slice, 
                    # we choose to not log such action for now.
                    self._parent_df.history.append_event("iloc", columns, rank_type="parent", child_df=None)
            else:
                # only some rows have been referenced
                self._parent_df.history.append_event("iloc", [], rank_type="parent", child_df=None)
        else:
            super(iLuxLocIndexer, self).__setitem__(key, value)


    def _getitem_axis(self, key, axis: int):
        ret_value = super(iLuxLocIndexer, self)._getitem_axis(key, axis)
        ret_value = self._lux_copymd(ret_value)
        ret_value._parent_df = self._parent_df 
        ret_value.history.append_event("iloc", [], rank_type="child", child_df=None)
        return ret_value

    def _getitem_tuple(self, tup: Tuple):
        ret_value = super(iLuxLocIndexer, self)._getitem_tuple(tup)
        ret_value = self._lux_copymd(ret_value)
        ret_value._parent_df = self._parent_df
        if self._parent_df is not None:
            columns = convert_indices_to_columns(self._parent_df.columns, tup)
            # inside the _getitem_tuple the function _getitem_axis might be called
            # at least when we call df.loc["cobra", ["shield", "max_speed"]]
            if ret_value.history.check_event(-1, op_name="iloc"):
                ret_value.history.edit_event(-1, "iloc", columns, rank_type="child", child_df=None)
            else:
                ret_value.history.append_event("iloc", columns, rank_type="child", child_df=None)
        return ret_value

    def _lux_copymd(self, ret_value):
        for attr in self._metadata:
            ret_value.__dict__[attr] = getattr(self, attr, None)
        
        ret_value.history = ret_value.history.copy()
        return ret_value
