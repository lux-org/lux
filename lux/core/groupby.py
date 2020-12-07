import pandas as pd

class LuxDataFrameGroupBy(pd.core.groupby.generic.DataFrameGroupBy):

    _metadata = [
        "_intent",
        "data_type_lookup",
        "data_type",
        "data_model_lookup",
        "data_model",
        "unique_values",
        "cardinality",
        "_rec_info",
        "_pandas_only",
        "_min_max",
        "plot_config",
        "_current_vis",
        "_widget",
        "_recommendation",
        "_prev",
        "_history",
        "_saved_export",
        "name",
    ]

    def __init__(self, *args, **kwargs):
        print("hi")
        super(LuxDataFrameGroupBy, self).__init__(*args, **kwargs)

    def aggregate(self, *args, **kwargs):
        print("go aggies")
        ret_val = super(LuxDataFrameGroupBy, self).aggregate(*args, **kwargs)
        for attr in self._metadata:
            ret_val.__dict__[attr] = getattr(self, attr, None)
        return ret_val

    agg = aggregate