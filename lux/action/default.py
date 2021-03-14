import lux
from lux.action.custom import custom
from lux.action.correlation import correlation
from lux.action.univariate import univariate
from lux.action.enhance import enhance
from lux.action.filter import add_filter
from lux.action.generalize import generalize
from lux.utils import utils
from lux.vis.VisList import VisList
from lux.interestingness.interestingness import interestingness


def register_default_actions():

    # display conditions for default actions
    no_vis = lambda ldf: (ldf.current_vis is None) or (
        ldf.current_vis is not None and len(ldf.current_vis) == 0
    )
    one_current_vis = lambda ldf: ldf.current_vis is not None and len(ldf.current_vis) == 1
    multiple_current_vis = lambda ldf: ldf.current_vis is not None and len(ldf.current_vis) > 1

    # globally register default actions
    lux.config.register_action("correlation", correlation, correlation_check)
    lux.config.register_action("distribution", univariate, distribution_check, "quantitative")
    lux.config.register_action("occurrence", univariate, occurence_check, "nominal")
    lux.config.register_action("temporal", univariate, temporal_check, "temporal")
    lux.config.register_action("geographical", univariate, no_vis, "geographical")

    lux.config.register_action("Enhance", enhance, enhance_check)
    lux.config.register_action("Filter", add_filter, one_current_vis)
    lux.config.register_action("Generalize", generalize, generalize_check)

    lux.config.register_action("Custom", custom, multiple_current_vis)


def generalize_check(ldf):
    filters = utils.get_filter_specs(ldf._intent)
    attributes = list(filter(lambda x: x.value == "" and x.attribute != "Record", ldf._intent))
    if (len(attributes) <= 1 or len(attributes) > 4) and len(filters) == 0:
        return False
    else:
        return ldf.current_vis is not None and len(ldf.current_vis) == 1


def correlation_check(ldf):
    if len(ldf) < 5:
        return False
    else:
        filter_specs = utils.get_filter_specs(ldf._intent)
        intent = [
            lux.Clause("?", data_model="measure"),
            lux.Clause("?", data_model="measure"),
        ]
        intent.extend(filter_specs)
        vlist = VisList(intent, ldf)
        if len(vlist) < 1:
            return False
        else:
            return (ldf.current_vis is None) or (
                ldf.current_vis is not None and len(ldf.current_vis) == 0
            )


def occurence_check(ldf):
    filter_specs = utils.get_filter_specs(ldf._intent)
    intent = [lux.Clause("?", data_type="nominal")]
    intent.extend(filter_specs)
    vlist = VisList(intent, ldf)
    for vis in vlist:
        vis.score = interestingness(vis, ldf)
    vlist.sort()

    if len(vlist) < 1:
        return False
    else:
        return (ldf.current_vis is None) or (ldf.current_vis is not None and len(ldf.current_vis) == 0)


def distribution_check(ldf):
    filter_specs = utils.get_filter_specs(ldf._intent)
    possible_attributes = [
        c
        for c in ldf.columns
        if ldf.data_type[c] == "quantitative" and ldf.cardinality[c] > 5 and c != "Number of Records"
    ]
    intent = [lux.Clause(possible_attributes)]
    intent.extend(filter_specs)
    vlist = VisList(intent, ldf)
    if len(vlist) < 1:
        return False
    else:
        return (ldf.current_vis is None) or (ldf.current_vis is not None and len(ldf.current_vis) == 0)


def temporal_check(ldf):
    filter_specs = utils.get_filter_specs(ldf._intent)
    intent = [lux.Clause("?", data_type="temporal")]
    intent.extend(filter_specs)
    vlist = VisList(intent, ldf)
    for vis in vlist:
        vis.score = interestingness(vis, ldf)
    vlist.sort()
    # Doesn't make sense to generate a line chart if there is less than 3 datapoints (pre-aggregated)
    if len(ldf) < 3:
        return False
    if len(vlist) < 1:
        return False
    else:
        return (ldf.current_vis is None) or (ldf.current_vis is not None and len(ldf.current_vis) == 0)


def enhance_check(ldf):
    filters = utils.get_filter_specs(ldf._intent)
    intent = ldf._intent.copy()
    attr_specs = list(filter(lambda x: x.value == "" and x.attribute != "Record", ldf._intent))
    if len(attr_specs) > 2:
        return False
    else:
        return ldf.current_vis is not None and len(ldf.current_vis) == 1
