def register_default_actions():
    import lux
    from lux.action.custom import custom
    from lux.action.correlation import correlation
    from lux.action.univariate import univariate
    from lux.action.enhance import enhance
    from lux.action.filter import add_filter
    from lux.action.generalize import generalize
    from lux.action.temporal import temporal

    # display conditions for default actions
    no_vis = lambda ldf: (ldf.current_vis is None) or (
        ldf.current_vis is not None and len(ldf.current_vis) == 0
    )
    one_current_vis = lambda ldf: ldf.current_vis is not None and len(ldf.current_vis) == 1
    multiple_current_vis = lambda ldf: ldf.current_vis is not None and len(ldf.current_vis) > 1

    # globally register default actions
    lux.config.register_action("correlation", correlation, no_vis)
    lux.config.register_action("distribution", univariate, no_vis, "quantitative")
    lux.config.register_action("occurrence", univariate, no_vis, "nominal")
    lux.config.register_action("temporal", temporal, no_vis)
    lux.config.register_action("geographical", univariate, no_vis, "geographical")

    lux.config.register_action("Enhance", enhance, one_current_vis)
    lux.config.register_action("Filter", add_filter, one_current_vis)
    lux.config.register_action("Generalize", generalize, one_current_vis)

    lux.config.register_action("Custom", custom, multiple_current_vis)
