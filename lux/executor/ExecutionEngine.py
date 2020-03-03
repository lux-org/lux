import lux 
from lux.view.ViewCollection import ViewCollection
class ExecutionEngine:
    def __init__(self):
        self.name = "ExecutionEngine"

    def __repr__(self):
        return f"<ExecutionEngine>"
    @staticmethod
    def execute( vc : ViewCollection, ldf : lux.LuxDataFrame):
        '''
        Given a ViewCollection, fetch the data required to render the view
        1) Apply filters
        2) Retreive relevant attribute
        3) return a DataFrame with relevant results
        '''
        ldf = ExecutionEngine.executeFilter(ldf)
        # TODO:Select relevant data based on attribute information
        return ldf 

    @staticmethod
    def executeFilter(ldf : lux.LuxDataFrame):
        return NotImplementedError