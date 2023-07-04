import pandas as pd


class LuxGroupByMixin:
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

    def aggregate(self, *args, **kwargs):
        ret_val = super().aggregate(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        return ret_val

    def _agg_general(self, *args, **kwargs):
        ret_val = super()._agg_general(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        return ret_val

    def _cython_agg_general(self, *args, **kwargs):
        ret_val = super()._cython_agg_general(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        return ret_val

    def get_group(self, *args, **kwargs):
        ret_val = super().get_group(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        ret_val.pre_aggregated = False  # Returned LuxDataFrame isn't pre_aggregated
        return ret_val

    def filter(self, *args, **kwargs):
        ret_val = super().filter(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        ret_val.pre_aggregated = False  # Returned LuxDataFrame isn't pre_aggregated
        return ret_val

    def apply(self, *args, **kwargs):
        ret_val = super().apply(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        ret_val.pre_aggregated = False  # Returned LuxDataFrame isn't pre_aggregated
        return ret_val

    def size(self, *args, **kwargs):
        ret_val = super().size(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        return ret_val

    def __getitem__(self, *args, **kwargs):
        ret_val = super().__getitem__(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        return ret_val

    agg = aggregate


class LuxDataFrameGroupBy(LuxGroupByMixin, pd.core.groupby.DataFrameGroupBy):
    pass


class LuxSeriesGroupBy(LuxGroupByMixin, pd.core.groupby.SeriesGroupBy):
    pass
