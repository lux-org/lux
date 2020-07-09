from lux.view.ViewCollection import ViewCollection
from lux.utils import utils
class Executor:
    """
    Abstract class for the execution engine that fetches data for a given view on a LuxDataFrame
    """    
    def __init__(self):
        self.name = "Executor"

    def __repr__(self):
        return f"<Executor>"
    @staticmethod
    def execute(view_collection:ViewCollection, ldf):
        return NotImplemented

    @staticmethod
    def execute_aggregate(view, ldf):
        return NotImplemented
    @staticmethod
    def execute_binning(view, ldf):
        return NotImplemented
        
    @staticmethod
    def execute_filter(view, ldf):
        return NotImplemented