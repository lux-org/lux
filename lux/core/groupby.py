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
        super(LuxGroupBy, self).__init__(*args, **kwargs)
        self._history = History(self)
        self._parent_df = None

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, history: History):
        self._history = history

    ####################
    ## Different aggs  #
    ####################
    def aggregate(self, func=None, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).aggregate(func, *args, **kwargs)
        ret_value = self._lux_copymd(ret_value)
        ret_value._parent_df = self

        if isinstance(func, str):
            ret_value.history.append_event(func, [], rank_type="child", child_df=None)

        # for some reason is_list_like({}) == True so MUST compare dict first
        elif is_dict_like(func):
            for col, aggs in func.items():
                if is_list_like(aggs):
                    for a in aggs:
                        ret_value.history.append_event(a, [col], rank_type="child", child_df=None)
                else:  # aggs is str
                    ret_value.history.append_event(aggs, [col], rank_type="child", child_df=None)

        elif is_list_like(func):
            for f_name in func:
                ret_value.history.append_event(f_name, [], rank_type="child", child_df=None)

        return ret_value

    agg = aggregate

    def _agg_general(self, *args, **kwargs):
        """
        this calls _cython_agg_general, if that fails calls self.aggregate
        """
        ret_value = super(LuxGroupBy, self)._agg_general(*args, **kwargs)
        ret_value = self._lux_copymd(ret_value)
        ret_value._parent_df = self

        return ret_value

    def _cython_agg_general(self, how: str, *args, **kwargs):
        ret_value = super(LuxGroupBy, self)._cython_agg_general(how, *args, **kwargs)
        ret_value = self._lux_copymd(ret_value)
        ret_value._parent_df = self

        return ret_value

    #################
    ## Utils, etc   #
    #################
    def _lux_copymd(self, ret_value):
        for attr in self._metadata:
            ret_value.__dict__[attr] = getattr(self, attr, None)

        ret_value.history = ret_value.history.copy()
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

    def filter(self, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).filter(*args, **kwargs)
        ret_value = self._lux_copymd(ret_value)
        ret_value.history.append_event("gb_filter", [], rank_type="child", child_df=None, filt_key=None)
        ret_value.pre_aggregated = False  # Returned LuxDataFrame isn't pre_aggregated
        ret_value._parent_df = self
        return ret_value

    def apply(self, *args, **kwargs):
        ret_value = super(LuxGroupBy, self).apply(*args, **kwargs)
        ret_value = self._lux_copymd(ret_value)
        ret_value.history.append_event("gb_apply", [], rank_type="child", child_df=None)
        ret_value.pre_aggregated = False  # Returned LuxDataFrame isn't pre_aggregated
        ret_value._parent_df = self
        return ret_value

    ##################
    ## agg functions #
    ##################
    def _eval_agg_function_lux(self, func_name: str, *args, **kwargs):
        with self.history.pause():
            method = getattr(super(LuxGroupBy, self), func_name)
            ret_value = method(*args, **kwargs)

        ret_value = self._lux_copymd(ret_value)
        ret_value.history.append_event(func_name, [], rank_type="child", child_df=None)
        ret_value._parent_df = self

        return ret_value

    def size(self, *args, **kwargs):
        return self._eval_agg_function_lux("size", *args, **kwargs)

    def mean(self, *args, **kwargs):
        return self._eval_agg_function_lux("mean", *args, **kwargs)

    def min(self, *args, **kwargs):
        return self._eval_agg_function_lux("min", *args, **kwargs)

    def max(self, *args, **kwargs):
        return self._eval_agg_function_lux("max", *args, **kwargs)

    def count(self, *args, **kwargs):
        return self._eval_agg_function_lux("count", *args, **kwargs)

    def sum(self, *args, **kwargs):
        return self._eval_agg_function_lux("sum", *args, **kwargs)

    def prod(self, *args, **kwargs):
        return self._eval_agg_function_lux("prod", *args, **kwargs)

    def median(self, *args, **kwargs):
        return self._eval_agg_function_lux("median", *args, **kwargs)

    def std(self, *args, **kwargs):
        return self._eval_agg_function_lux("std", *args, **kwargs)

    def var(self, *args, **kwargs):
        return self._eval_agg_function_lux("var", *args, **kwargs)

    def sem(self, *args, **kwargs):
        return self._eval_agg_function_lux("sem", *args, **kwargs)


class LuxDataFrameGroupBy(LuxGroupBy, pd.core.groupby.generic.DataFrameGroupBy):
    def __init__(self, *args, **kwargs):
        super(LuxDataFrameGroupBy, self).__init__(*args, **kwargs)


class LuxSeriesGroupBy(LuxGroupBy, pd.core.groupby.generic.SeriesGroupBy):
    def __init__(self, *args, **kwargs):
        super(LuxSeriesGroupBy, self).__init__(*args, **kwargs)
