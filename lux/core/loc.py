import pandas as pd
from lux.history.history import History
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

    def _getitem_axis(self, key, axis: int):
        ret_value = super(LuxLocIndexer, self)._getitem_axis(key, axis)
        ret_value = self._lux_copymd(ret_value)
        ret_value._parent_df = self
        ret_value.history.append_event("loc", [], rank_type="child", child_df=None)
        return ret_value

    def _getitem_tuple(self, tup: Tuple):
        ret_value = super(LuxLocIndexer, self)._getitem_tuple(tup)
        ret_value = self._lux_copymd(ret_value)
        ret_value._parent_df = self
        columns = []
        if isinstance(tup[1], str):
            columns.append(tup[1])
        elif isinstance(tup[1], list):
            columns.extend(tup[1])
        ret_value.history.append_event("loc", columns, rank_type="child", child_df=None)
        return ret_value

    def _lux_copymd(self, ret_value):
        for attr in self._metadata:
            ret_value.__dict__[attr] = getattr(self, attr, None)
        
        ret_value.history = ret_value.history.copy()
        return ret_value


