from lux.interestingness.interestingness import interestingness
import lux
from lux.executor.PandasExecutor import PandasExecutor
from lux.executor.SQLExecutor import SQLExecutor
#for benchmarking
import time

def custom(ldf):
    '''
    Generates user-defined views based on the intent.

    Parameters
    ----------
    ldf : lux.luxDataFrame.LuxDataFrame
        LuxDataFrame with underspecified intent.

    Returns
    -------
    recommendations : Dict[str,obj]
        object with a collection of visualizations that result from the Distribution action.
    '''
    recommendation = {"action": "Current Vis",
                      "description": "Shows the list of visualizations generated based on user specified intent"}

    recommendation["collection"] = ldf.current_vis

    vc = ldf.current_vis
    PandasExecutor.execute(vc, ldf)
    for view in vc: 
        view.score = interestingness(view,ldf)
    # ldf.clear_intent()
    vc.sort(remove_invalid=True)
    return recommendation