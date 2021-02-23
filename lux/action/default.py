def register_default_actions():
    import lux
    from lux.action.custom import custom
    from lux.action.correlation import correlation
    from lux.action.univariate import univariate
    from lux.action.enhance import enhance
    from lux.action.filter import add_filter
    from lux.action.generalize import generalize

    # display conditions for default actions
    no_vis = lambda ldf: (ldf.current_vis is None) or (
        ldf.current_vis is not None and len(ldf.current_vis) == 0
    )
    one_current_vis = lambda ldf: ldf.current_vis is not None and len(ldf.current_vis) == 1
    multiple_current_vis = lambda ldf: ldf.current_vis is not None and len(ldf.current_vis) > 1

    # globally register default actions
    lux.config.register_action("Correlation", correlation, no_vis)
    lux.config.register_action("Distribution", univariate, no_vis, "quantitative")
    lux.config.register_action("Occurrence", univariate, no_vis, "nominal")
    lux.config.register_action("Temporal", univariate, no_vis_temporal, "temporal")

    lux.config.register_action("Enhance", enhance, one_current_vis)
    lux.config.register_action("Filter", add_filter, one_current_vis)
    lux.config.register_action("Generalize", generalize, one_current_vis)

    lux.config.register_action("Custom", custom, multiple_current_vis)

"""
Display condition function to check whether or not calculations for temporal action is needed.
"""
def no_vis_temporal(ldf):
    from lux.utils.date_utils import is_datetime_series
    if (ldf.current_vis is None or (ldf.current_vis is not None and len(ldf.current_vis) == 0)):
        if (any([is_datetime_series(col) for col in ldf])):
            return True
    else:
        return False