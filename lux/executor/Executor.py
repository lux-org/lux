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