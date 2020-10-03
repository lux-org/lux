from lux.interestingness.interestingness import interestingness
import lux
from lux.executor.PandasExecutor import PandasExecutor
from lux.executor.SQLExecutor import SQLExecutor

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

def custom_actions(ldf):
    if (lux.actions.__len__() > 0):
        recommendations = []
        for action_name in lux.actions.__dir__():
            validator = lux.actions.__getattr__(action_name).validator 
            if validator is None or (validator is not None and validator(ldf)):
                args = lux.actions.__getattr__(action_name).args
                if args:
                    function = lux.actions.__getattr__(action_name).function(ldf, args)
                else:
                    function = lux.actions.__getattr__(action_name).function(ldf)
                recommendation = {"action":function["action"], "description":function["description"]}
                recommendation["collection"] = function["collection"]
                recommendations.append(recommendation)
        return recommendations
    else:
        return []
