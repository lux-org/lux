from .context import lux
import pytest
import pandas as pd
from lux.history.history import History 
def test_append_event():
    history = History(ldf=None)
    history.append_event("describe", ["Name", "Cylinders"],  rank_type="parent")
    assert len(history) == 1, "The length of the history should be that of the events"
    new_event = history[0]
    assert new_event.op_name == "describe", "The operartion name for the newly added event should be `describe`"
    assert new_event.cols == ["Name", "Cylinders"], "The columns for the newly added event should be recorded"
    assert new_event.kwargs.get("rank_type", None) == "parent", "Kwargs parameters should be also recorded in the event"

    assert lux.config.update_actions["flag"], "We should update actions after the history is updated"

def test_edit_event():
    history = History(ldf=None)
    history.append_event("describe", ["Name", "Cylinders"],  rank_type="parent")
    history.edit_event(0, "dropna", ["Origin", "Brand"], rank_type="child")
    edited_event = history[0]
    assert edited_event.op_name == "dropna", "The operartion name for the newly added event should be `dropna`"
    assert edited_event.cols == ["Origin", "Brand"], "The columns for the newly added event should also be modifed"
    assert edited_event.kwargs.get("rank_type", None) == "child", "Kwargs parameters should be also modified in the event"

def test_check_event():
    history = History(ldf=None)
    history.append_event("describe", ["Name", "Cylinders"],  rank_type="parent")
    assert history.check_event(0, op_name="describe", cols=["Name", "Cylinders"])
    assert not history.check_event(0, op_name="describe", cols=["Name"])
    assert not history.check_event(0, op_name="dropna", cols=["Name", "Cylinders"])

def test_delete_at():
    history = History(ldf=None)
    history.append_event("describe", ["Name", "Cylinders"],  rank_type="parent")
    history.append_event("dropna", ["Origin", "Brand"],  rank_type="child")
    history.append_event("loc", ["Weights"])

    with history.pause():
        deleted_event = history.delete_at(2)
        assert (deleted_event is None), "Events could not be deleted when the history is frozen"

    deleted_event = history.delete_at(2)
    assert deleted_event.op_name == "loc", "Events should be deleted when the history is unfrozen"

def test_get_cleaned_event():
    history = History(ldf=None)
    history.append_event("describe", ["Name", "Cylinders"],  rank_type="parent")
    history.append_event("dropna", ["Origin", "Brand"],  rank_type="child")
    history.append_event("loc", ["Weights"])
    cleaned_events = history.get_cleaned_events()
    assert len(cleaned_events) == 2

def test_clear():
    history = History(ldf=None)
    history.append_event("describe", ["Name", "Cylinders"],  rank_type="parent")
    history.append_event("dropna", ["Origin", "Brand"],  rank_type="child")

    with history.pause():
        history.clear()
    assert len(history) == 2, "The history could not be cleared when it is frozen"

    history.clear()
    assert len(history) == 0, "The history should be cleared when it is unfrozen"


def test_valid_cols():
    history = History(ldf=None)
    history.append_event("describe", ["Name", "Cylinders"],  rank_type="parent")
    lookfor_event = history.get_hist_item(0, ["Name", "Origin"])
    assert lookfor_event.cols == ["Name"]

def test_freeze():
    history = History(ldf=None)
    history.freeze()
    history.append_event("describe", ["Name", "Cylinders"],  rank_type="parent")
    assert len(history) == 0, "No event could be logged when the history is frozen"

    history.unfreeze()
    history.append_event("describe", ["Name", "Cylinders"],  rank_type="parent")
    assert len(history) == 1, "Events could be logged when the history is unfrozen"

    with history.pause():
        history.append_event("describe", ["Name", "Cylinders"],  rank_type="parent")
    assert len(history) == 1, "No more events could be logged when the codes are within the pause scope"

    history.append_event("describe", ["Name", "Cylinders"],  rank_type="parent")
    assert len(history) == 2, "Events could be logged when the codes are out of the pause scope"

def test_get_weights():
    # for now, we still use the execution count provided by the kernel
    # so we are not able to check the decay between cells. 
    history = History(ldf=None)
    history.append_event("describe", ["Name", "Cylinders"],  rank_type="parent")
    history.append_event("dropna", ["Origin", "Brand"],  rank_type="child")
    history.append_event("loc", ["Weights"])
    weights = history.get_weights()
    assert weights[-1] > weights[-2] > weights[-3], "There should be some decay for weights of events in the same cell"

    history = History(ldf=None)
    history.append_event("assign", ["Weights"])
    history.append_event("dropna", ["Origin", "Brand"], rank_type="child")
    history.append_event("col_ref", ["Name"])
    
    weights = history.get_weights()
    assert weights[0] > weights[1] > weights[2], "The base weight for the assign event is higher than those for ordinary events, which are, however, higher than that the col_ref event."

def test_implicit_intent():
    history = History(ldf=None)
    history.append_event("describe", ["Name", "Cylinders"],  rank_type="parent")
    history.append_event("dropna", ["Name", "Brand"],  rank_type="child")
    history.append_event("loc", ["Weights"])
    implict_cols = history.get_implicit_intent(["Name", "Weights", "Brand"])
    assert implict_cols == ["Name", "Weights", "Brand"]

def test_most_recent_event():
    history = History(ldf=None)
    history.append_event("loc", ["Weights"])
    history.append_event("dropna", ["Name", "Brand"],  rank_type="child")
    history.append_event("describe", ["Name", "Cylinders"],  rank_type="parent")
    mre = history.get_mre(["Name"])[0]
    assert mre.op_name == "dropna", "The most recent event should be the first non-parent event"


