from lux._config import CONFIG


def register_default_actions():
    from lux.action.custom import custom
    from lux.action.correlation import correlation
    from lux.action.univariate import univariate
    from lux.action.enhance import enhance
    from lux.action.filter import add_filter
    from lux.action.generalize import generalize
    from lux.action.temporal import temporal

    # display conditions for default actions
    def no_vis(ldf): return (ldf.lux.current_vis is None) or (
        ldf.lux.current_vis is not None and len(ldf.lux.current_vis) == 0
    )

    def one_current_vis(ldf): return ldf.lux.current_vis is not None and len(
        ldf.lux.current_vis) == 1

    def multiple_current_vis(
        ldf): return ldf.lux.current_vis is not None and len(ldf.lux.current_vis) > 1

    # globally register default actions
    CONFIG.register_action("correlation", correlation, no_vis)
    CONFIG.register_action(
        "distribution", univariate, no_vis, "quantitative")
    CONFIG.register_action("occurrence", univariate, no_vis, "nominal")
    CONFIG.register_action("temporal", temporal, no_vis)
    CONFIG.register_action(
        "geographical", univariate, no_vis, "geographical")

    CONFIG.register_action("Enhance", enhance, one_current_vis)
    CONFIG.register_action("Filter", add_filter, one_current_vis)
    CONFIG.register_action("Generalize", generalize, one_current_vis)

    CONFIG.register_action("Custom", custom, multiple_current_vis)
