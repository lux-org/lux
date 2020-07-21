from lux.interestingness.interestingness import interestingness
import lux
from lux.executor.PandasExecutor import PandasExecutor
from lux.executor.SQLExecutor import SQLExecutor
#for benchmarking
import time

def custom(ldf):
    '''
    Generates user-defined views based on the context.

    Parameters
    ----------
    ldf : lux.luxDataFrame.LuxDataFrame
        LuxDataFrame with underspecified context.

    Returns
    -------
    recommendations : Dict[str,obj]
        object with a collection of visualizations that result from the Distribution action.
    '''
    recommendation = {"action": "Current Context",
                      "description": "Shows the VisList defined by the current context"}

    recommendation["collection"] = ldf.current_context

    vc = ldf.current_context
    PandasExecutor.execute(vc, ldf)
    for view in vc: 
        view.score = interestingness(view,ldf)
    # ldf.clear_context()
    vc.sort(remove_invalid=True)
    return recommendation