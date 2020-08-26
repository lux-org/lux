from .context import lux
import pytest
import pandas as pd

# Test suite for checking if the expected errors and warnings are showing up correctly
def test_context_str_error():
    df = pd.read_csv("lux/data/college.csv")
    with pytest.raises(TypeError,match="Input intent must be a list"):
        df.set_intent("bad string input")
def test_export_b4_widget_created():
    df = pd.read_csv("lux/data/college.csv")
    with pytest.warns(UserWarning,match="No widget attached to the dataframe"):
        df.exported
def test_bad_filter():
    df = pd.read_csv("lux/data/college.csv")
    with pytest.warns(UserWarning,match="Lux can not operate on an empty dataframe"):
        df[df["Region"]=="asdfgh"]._repr_html_()
# Test Properties with Private Variables Readable but not Writable
def test_vis_private_properties():
    from lux.vis.Vis import Vis
    df = pd.read_csv("lux/data/car.csv")
    vis = Vis(["Horsepower","Weight"],df)
    vis._repr_html_()
    assert isinstance(vis.data,lux.core.frame.LuxDataFrame)
    with pytest.raises(AttributeError,match="can't set attribute"):
        vis.data = "some val"

    assert isinstance(vis.code,dict)
    with pytest.raises(AttributeError,match="can't set attribute"):
        vis.code = "some val"
    
    assert isinstance(vis.min_max,dict)
    with pytest.raises(AttributeError,match="can't set attribute"):
        vis.min_max = "some val"

    assert vis.mark =="scatter"
    with pytest.raises(AttributeError,match="can't set attribute"):
        vis.mark = "some val"
    
