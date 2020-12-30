def register_default_actions():
    import lux
    from lux.action.custom import custom
    from lux.action.correlation import correlation
    from lux.action.univariate import univariate
    from lux.action.enhance import enhance
    from lux.action.filter import add_filter
    from lux.action.generalize import generalize

    print("Register default actions")
    # display conditions for default actions
    no_vis = lambda ldf: (ldf.current_vis is None) or (
        ldf.current_vis is not None and len(ldf.current_vis) == 0
    )
    one_current_vis = lambda ldf: ldf.current_vis is not None and len(ldf.current_vis) == 1
    multiple_current_vis = lambda ldf: ldf.current_vis is not None and len(ldf.current_vis) > 1

    # globally register default actions
    lux.register_action("correlation", correlation, no_vis)
    lux.register_action("distribution", univariate, no_vis, "quantitative")
    lux.register_action("occurrence", univariate, no_vis, "nominal")
    lux.register_action("temporal", univariate, no_vis, "temporal")

    lux.register_action("Enhance", enhance, one_current_vis)
    lux.register_action("Filter", add_filter, one_current_vis)
    lux.register_action("Generalize", generalize, one_current_vis)

    lux.register_action("Custom", custom, multiple_current_vis)
