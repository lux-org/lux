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
    def execute(vis_collection:VisList, ldf):
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

    @staticmethod
    def compute_data_model(self):
        return NotImplemented

    def mapping(self, rmap):
        group_map = {}
        for val in ["quantitative", "id", "ordinal", "nominal", "temporal"]:
            group_map[val] = list(filter(lambda x: rmap[x] == val, rmap))
        return group_map

    def reverseMapping(self, map):
        reverse_map = {}
        for valKey in map:
            for val in map[valKey]:
                reverse_map[val] = valKey
        return reverse_map