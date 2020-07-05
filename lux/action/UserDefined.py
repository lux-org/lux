from lux.interestingness.interestingness import interestingness
import lux
from lux.executor.PandasExecutor import PandasExecutor
from lux.executor.SQLExecutor import SQLExecutor
#for benchmarking
import time

def userDefined(ldf):
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
    recommendation = {"action": "View Collection",
                      "description": "Shows a view collection defined by the context"}
    recommendation["collection"] = ldf.view_collection

    vc = ldf.view_collection
    PandasExecutor.execute(vc, ldf)
    for view in vc: 
        view.score = interestingness(view,ldf)
    # ldf.clearContext()
    vc.sort(removeInvalid=True)
    return recommendation