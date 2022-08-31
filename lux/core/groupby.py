import pandas as pd
import cudf
frame = pd.core.groupby.groupby.GroupBy if backend.set_back !="holoviews" else cudf.core.groupby.GroupBy
class LuxGroupBy(frame):

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

    def aggregate(self, *args, **kwargs):
        ret_val = super(LuxGroupBy, self).aggregate(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        return ret_val

    def _agg_general(self, *args, **kwargs):
        ret_val = super(LuxGroupBy, self)._agg_general(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        return ret_val

    def _cython_agg_general(self, *args, **kwargs):
        ret_val = super(LuxGroupBy, self)._cython_agg_general(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        return ret_val

    def get_group(self, *args, **kwargs):
        ret_val = super(LuxGroupBy, self).get_group(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        ret_val.pre_aggregated = False  # Returned LuxDataFrame isn't pre_aggregated
        return ret_val

    def filter(self, *args, **kwargs):
        ret_val = super(LuxGroupBy, self).filter(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        ret_val.pre_aggregated = False  # Returned LuxDataFrame isn't pre_aggregated
        return ret_val

    def apply(self, *args, **kwargs):
        ret_val = super(LuxGroupBy, self).apply(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        ret_val.pre_aggregated = False  # Returned LuxDataFrame isn't pre_aggregated
        return ret_val

    def size(self, *args, **kwargs):
        ret_val = super(LuxGroupBy, self).size(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        return ret_val

    def __getitem__(self, *args, **kwargs):
        ret_val = super(LuxGroupBy, self).__getitem__(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        return ret_val

    agg = aggregate


if backend.set_back !="holoviews":
    df_frame = pd.core.groupby.generic.DataFrameGroupBy
    series_frame = pd.core.groupby.generic.SeriesGroupBy
else:
    df_frame = cudf.core.groupby.groupby.DataFrameGroupBy
    series_frame = cudf.core.groupby.groupby.SeriesGroupBy
    
class LuxDataFrameGroupBy(LuxGroupBy, df_frame):
    def __init__(self, *args, **kwargs):
        super(LuxDataFrameGroupBy, self).__init__(*args, **kwargs)


class LuxSeriesGroupBy(LuxGroupBy, series_frame):
    def __init__(self, *args, **kwargs):
        super(LuxSeriesGroupBy, self).__init__(*args, **kwargs)
