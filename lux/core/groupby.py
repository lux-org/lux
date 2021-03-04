import pandas as pd


class LuxDataFrameGroupBy(pd.core.groupby.generic.DataFrameGroupBy):

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
        super(LuxDataFrameGroupBy, self).__init__(*args, **kwargs)

    def aggregate(self, *args, **kwargs):
        ret_val = super(LuxDataFrameGroupBy, self).aggregate(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        return ret_val

    def _agg_general(self, *args, **kwargs):
        ret_val = super(LuxDataFrameGroupBy, self)._agg_general(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        return ret_val

    def _cython_agg_general(self, *args, **kwargs):
        ret_val = super(LuxDataFrameGroupBy, self)._cython_agg_general(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        return ret_val

    def get_group(self, *args, **kwargs):
        ret_val = super(LuxDataFrameGroupBy, self).get_group(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        ret_val.pre_aggregated = False  # Returned LuxDataFrame isn't pre_aggregated
        return ret_val

    def filter(self, *args, **kwargs):
        ret_val = super(LuxDataFrameGroupBy, self).filter(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        ret_val.pre_aggregated = False  # Returned LuxDataFrame isn't pre_aggregated
        return ret_val

    def apply(self, *args, **kwargs):
        ret_val = super(LuxDataFrameGroupBy, self).apply(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        ret_val.pre_aggregated = False  # Returned LuxDataFrame isn't pre_aggregated
        return ret_val

    def size(self, *args, **kwargs):
        ret_val = super(LuxDataFrameGroupBy, self).size(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        return ret_val

    def __getitem__(self, *args, **kwargs):
        ret_val = super(LuxDataFrameGroupBy, self).__getitem__(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        return ret_val

    agg = aggregate
