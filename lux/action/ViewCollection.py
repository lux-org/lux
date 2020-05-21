from lux.interestingness.interestingness import interestingness
import lux
from lux.executor.PandasExecutor import PandasExecutor
from lux.executor.SQLExecutor import SQLExecutor
#for benchmarking
import time

def viewCollection(ldf):
    '''
    Generates bar chart distributions of different attributes in the dataset.

    Parameters
    ----------
    ldf : lux.luxDataFrame.LuxDataFrame
        LuxDataFrame with underspecified context.

    dataTypeConstraint: str
        The variable that controls the type of distribution chart that will be rendered.

    Returns
    -------
    recommendations : Dict[str,obj]
        object with a collection of visualizations that result from the Distribution action.
    '''
    recommendation = {"action": "View Collection",
                      "description": "Shows a view collection defined by the context"}
    recommendation["collection"] = ldf.viewCollection

    vc = ldf.viewCollection
    PandasExecutor.execute(vc, ldf)

    ldf.clearContext()
    return recommendation