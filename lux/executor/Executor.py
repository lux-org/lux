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

from lux.vis.VisList import VisList
from lux.utils import utils


class Executor:
    """
    Abstract class for the execution engine that fetches data for a given vis on a LuxDataFrame
    """

    def __init__(self):
        self.name = "Executor"

    def __repr__(self):
        return f"<Executor>"

    @staticmethod
    def execute(vis_collection: VisList, ldf):
        return NotImplemented

    @staticmethod
    def execute_aggregate(vis, ldf):
        return NotImplemented

    @staticmethod
    def execute_binning(vis, ldf):
        return NotImplemented

    @staticmethod
    def execute_filter(vis, ldf):
        return NotImplemented

    @staticmethod
    def compute_stats(self):
        return NotImplemented

    @staticmethod
    def compute_data_type(self):
        return NotImplemented

    # @staticmethod
    # def compute_data_model(self):
    #     return NotImplemented

    def mapping(self, rmap):
        group_map = {}
        for val in ["quantitative", "id", "nominal", "temporal", "geographical"]:
            group_map[val] = list(filter(lambda x: rmap[x] == val, rmap))
        return group_map

    def reverseMapping(self, map):
        reverse_map = {}
        for valKey in map:
            for val in map[valKey]:
                reverse_map[val] = valKey
        return reverse_map

    def invert_data_type(self, data_type):
        return self.mapping(data_type)

    def compute_data_model(self, data_type):
        data_type_inverted = self.invert_data_type(data_type)
        data_model = {
            "measure": data_type_inverted["quantitative"],
            "dimension": data_type_inverted["nominal"]
            + data_type_inverted["temporal"]
            + data_type_inverted["id"]
            + data_type_inverted["geographical"],
        }
        return data_model

    def compute_data_model_lookup(self, data_type):
        return self.reverseMapping(self.compute_data_model(data_type))
