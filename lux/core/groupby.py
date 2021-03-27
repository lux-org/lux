import pandas as pd
from pandas.core.dtypes.common import is_list_like, is_dict_like
from lux.history.history import History

from IPython.core.debugger import set_trace

class LuxGroupBy(pd.core.groupby.groupby.GroupBy):

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
        "_saved_export",
        "_sampled",
        "_toggle_pandas_display",
        "_message",
        "_pandas_only",
        "pre_aggregated",
        "_type_override",
    ]

    def __init__(self, *args, **kwargs):
        super(LuxGroupBy, self).__init__(*args, **kwargs)
        self._history = History(self) 

    
   
    ####################
    ## Different aggs  # 
    ####################
    def aggregate(self, func=None, *args, **kwargs):

        # TODO use same copy scheme from frame
        ret_value = super(LuxGroupBy, self).aggregate(func, *args, **kwargs)
        ret_value = self._lux_copymd(ret_value)

        # for some reason is_list_like(dict) == True so MUST compare dict first 
        if is_dict_like(func):
            for i, (col, aggs) in enumerate(func.items()):
                decay = True
                if i > 0: decay = False # only decay for first item

                if is_list_like(aggs):
                    for a in aggs:
                        ret_value._history.append_event(a, [col], decay=decay, rank_type="child", child_df=None)
                        decay = False
                else: # is aggs is str
                    ret_value._history.append_event(aggs, [col], decay=decay, rank_type="child", child_df=None)
        
        elif is_list_like(func):
            for i, f_name in enumerate(func):
                decay = True
                if i > 0: decay = False # only decay for first item
                ret_value._history.append_event(f_name, [], decay=decay, rank_type="child", child_df=None)

        return ret_value
    
    agg = aggregate

    def _agg_general(self, *args, **kwargs):
        """
        this calls _cython_agg_general, if that fails calls self.aggregate
        """
        ret_value = super(LuxGroupBy, self)._agg_general(*args, **kwargs)
        ret_value = self._lux_copymd(ret_value, force=True)

        # ret_value._history.append_event(kwargs["alias"], [], rank_type="child", child_df=None)

        return ret_value

    def _cython_agg_general(self, how:str, *args, **kwargs):
        ret_value = super(LuxGroupBy, self)._cython_agg_general(how, *args, **kwargs)
        ret_value = self._lux_copymd(ret_value)

        # ret_value._history.append_event(how, [], rank_type="child", child_df=None)

        return ret_value
    
    #################
    ## Utils, etc   # 
    #################
    def _lux_copymd(self, ret_value, force=False):
        old_history = ret_value._history
        for attr in self._metadata:
            ret_value.__dict__[attr] = getattr(self, attr, None)
        
        if force or ((len(old_history) == 0) and ret_value._history is not None):
            ret_value._history = ret_value._history.copy()
        else:
            ret_value._history = old_history # restore 

        return ret_value

    def get_group(self, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).get_group(*args, **kwargs)
        ret_value = self._lux_copymd(ret_value)
        ret_value.pre_aggregated = False  # Returned LuxDataFrame isn't pre_aggregated
        return ret_value

    def __getitem__(self, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).__getitem__(*args, **kwargs)
        ret_value = self._lux_copymd(ret_value)
        return ret_value
    
    ##################
    ## agg functions # 
    ##################
    def filter(self, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).filter(*args, **kwargs)
        ret_value = self._lux_copymd(ret_value)
        ret_value.pre_aggregated = False  # Returned LuxDataFrame isn't pre_aggregated
        return ret_value

    def apply(self, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).apply(*args, **kwargs)
        ret_value = self._lux_copymd(ret_value)
        ret_value.pre_aggregated = False  # Returned LuxDataFrame isn't pre_aggregated
        return ret_value

    def size(self, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).size(*args, **kwargs)
        ret_value = self._lux_copymd(ret_value, force=True) # not copied over otherwise
        ret_value._history.append_event("size", [], rank_type="child", child_df=None)
        ret_value.pre_aggregated = True
        return ret_value

    def mean(self, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).mean(*args, **kwargs)
        ret_value._history.append_event("mean", [], rank_type="child", child_df=None)
        ret_value.pre_aggregated = True
        return ret_value
    
    def min(self, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).min(*args, **kwargs)
        ret_value._history.append_event("min", [], rank_type="child", child_df=None)
        ret_value.pre_aggregated = True
        return ret_value
    
    def max(self, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).max(*args, **kwargs)
        ret_value._history.append_event("max", [], rank_type="child", child_df=None)
        ret_value.pre_aggregated = True
        return ret_value

    def count(self, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).count(*args, **kwargs)
        ret_value = self._lux_copymd(ret_value) # not copied over otherwise
        ret_value._history.append_event("count", [], rank_type="child", child_df=None)
        ret_value.pre_aggregated = True
        return ret_value
    
    def sum(self, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).sum(*args, **kwargs)
        ret_value._history.append_event("sum", [], rank_type="child", child_df=None)
        ret_value.pre_aggregated = True
        return ret_value
    
    def prod(self, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).prod(*args, **kwargs)
        ret_value._history.append_event("prod", [], rank_type="child", child_df=None)
        ret_value.pre_aggregated = True
        return ret_value
    
    def median(self, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).median(*args, **kwargs)
        ret_value = self._lux_copymd(ret_value) # not copied over otherwise
        ret_value._history.append_event("median", [], rank_type="child", child_df=None)
        ret_value.pre_aggregated = True
        return ret_value
    
    def std(self, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).std(*args, **kwargs)
        ret_value = self._lux_copymd(ret_value) # not copied over otherwise
        ret_value._history.append_event("std", [], rank_type="child", child_df=None)
        ret_value.pre_aggregated = True
        return ret_value

    def var(self, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).var(*args, **kwargs)
        ret_value._history.append_event("var", [], rank_type="child", child_df=None)
        ret_value.pre_aggregated = True
        return ret_value
    
    def sem(self, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).sem(*args, **kwargs)
        ret_value = self._lux_copymd(ret_value) # not copied over otherwise
        # ret_value._history.edit_event(-1, "sem", [], rank_type="child", child_df=None) # sem calls std so want to edit 
        ret_value._history.append_event("sem", [], rank_type="child", child_df=None)
        ret_value.pre_aggregated = True
        return ret_value


class LuxDataFrameGroupBy(LuxGroupBy, pd.core.groupby.generic.DataFrameGroupBy):
    def __init__(self, *args, **kwargs):
        super(LuxDataFrameGroupBy, self).__init__(*args, **kwargs)


class LuxSeriesGroupBy(LuxGroupBy, pd.core.groupby.generic.SeriesGroupBy):
    def __init__(self, *args, **kwargs):
        super(LuxSeriesGroupBy, self).__init__(*args, **kwargs)