from lux.interestingness.interestingness import interestingness
import lux
from lux.executor.PandasExecutor import PandasExecutor
from lux.executor.SQLExecutor import SQLExecutor
#for benchmarking
import time

def custom(ldf):
    '''
    Generates user-defined vis based on the intent.

    Parameters
    ----------
    ldf : lux.core.frame
        LuxDataFrame with underspecified intent.

    Returns
    -------
    recommendations : Dict[str,obj]
        object with a collection of visualizations that result from the Distribution action.
    '''
    recommendation = {"action": "Current Vis",
                      "description": "Shows the list of visualizations generated based on user specified intent"}

    recommendation["collection"] = ldf.current_vis

    vlist = ldf.current_vis
    PandasExecutor.execute(vlist, ldf)
    for vis in vlist: 
        vis.score = interestingness(vis,ldf)
    # ldf.clear_intent()
    vlist.sort(remove_invalid=True)
    return recommendation