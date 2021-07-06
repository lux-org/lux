import lux
from IPython.core.debugger import set_trace


def rename_from_history(child, parent):
    """
    Used if a new ldf is created from a series. We want to rename the columns of this new ldf


    Parameters
    ----------
    child : LuxDataFrame
        child that was created from parent

    parent: LuxDataFrame
        parent that we want to propogate the name from

    Updates child in place so no return
    """
    try:
        # this only applies with single column from series
        if len(child.columns) == 1:

            if (
                isinstance(parent, lux.core.series.LuxSeries)
                and parent.name is not None
                and parent.name != " "
            ):
                c = parent.name
            else:
                mre = child.history._events[-1]
                c = mre.cols[0] if len(mre.cols) else mre.op_name

            child.rename(columns={child.columns[0]: c}, inplace=True)  # MUST be inplace

    except IndexError:
        ...
