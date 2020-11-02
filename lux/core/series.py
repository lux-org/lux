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


class LuxSeries(pd.Series):
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
    ]

    def __init__(self, *args, **kw):
        super(LuxSeries, self).__init__(*args, **kw)

    @property
    def _constructor(self):
        return LuxSeries

    @property
    def _constructor_expanddim(self):
        from lux.core.frame import LuxDataFrame

        def f(*args, **kwargs):
            df = LuxDataFrame(*args, **kwargs)
            for attr in self._metadata:
                df.__dict__[attr] = getattr(self, attr, None)
            return df

        f._get_axis_number = super(LuxSeries, self)._get_axis_number
        return f
