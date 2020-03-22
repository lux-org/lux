from lux.view.ViewCollection import ViewCollection
class ExecutionEngine:
    def __init__(self):
        self.name = "ExecutionEngine"
    def __repr__(self):
        return f"<ExecutionEngine>"
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