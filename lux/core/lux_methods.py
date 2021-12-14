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
import typing as tp
from lux.utils.utils import get_all_annotations


# ------------------------------------------------------------------------------
# Override Pandas
# ------------------------------------------------------------------------------


class LuxMethods:
    _intent: tp.Any
    _inferred_intent: tp.Any
    _data_type: tp.Any
    unique_values: tp.Any
    cardinality: tp.Any
    _rec_info: tp.Any
    _min_max: tp.Any
    # pending find + replace
    _current_vis: tp.Any
    _widget: tp.Any
    _recommendation: tp.Any
    _history: tp.Any
    _saved_export: tp.Any
    _sampled: tp.Any
    _toggle_pandas_display: tp.Any
    _message: tp.Any
    _pandas_only: tp.Any
    pre_aggregated: tp.Any
    _type_override: tp.Any
    plotting_style: tp.Any
    name: tp.Any
    _compiled: bool
    output: tp.Any
    _length: tp.Optional[int]
    _metadata_fresh: bool

    @classmethod
    def from_lux_object(cls, field: str, obj: tp.Any, other: "LuxMethods"):
        annotations = get_all_annotations(cls, bound=LuxMethods)
        attributes = {}

        for annotation_field in annotations:
            attributes[annotation_field] = getattr(
                other, annotation_field, None)

        attributes[field] = obj

        lux_methods = cls.__new__(cls)
        lux_methods.__dict__.update(attributes)
        return lux_methods
