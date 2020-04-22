from lux.view.ViewCollection import ViewCollection
from lux.utils import utils
class Executor:
    def __init__(self):
        self.name = "Executor"

    def __repr__(self):
        return f"<Executor>"
    @staticmethod
    def execute(viewCollection:ViewCollection, ldf):
        return NotImplemented

    @staticmethod
    def executeAggregate(view, ldf):
        return NotImplemented
    @staticmethod
    def executeBinning(view, ldf):
        return NotImplemented
        
    @staticmethod
    def executeFilter(view, ldf):
        return NotImplemented