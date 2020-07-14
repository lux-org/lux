from .context import lux
import pytest
import pandas as pd

def test_view_collection():
    df = pd.read_csv("lux/data/olympic.csv")
    from lux.vis.VisCollection import VisCollection
    vc = VisCollection(["Height","SportType=Ball","?"],df)
    view_with_year = list(filter(lambda x: x.get_attr_by_attr_name("Year")!=[],vc))[0]
    assert view_with_year.get_attr_by_channel("x")[0].attribute=="Year"
    assert len(vc) == len(df.columns) -1 -1 #remove 1 for view with same filter attribute and remove 1 view with for same attribute
    vc = VisCollection(["Height","?"],df)
    assert len(vc) == len(df.columns) -1 #remove 1 for view with for same attribute

def test_view_collection_set_query():
    df = pd.read_csv("lux/data/olympic.csv")
    from lux.vis.VisCollection import VisCollection
    vc = VisCollection(["Height","SportType=Ice","?"],df)
    vc.set_specs(["Height","SportType=Boat","?"])
    for v in vc.collection: 
        filter_vspec = list(filter(lambda x: x.channel=="",v.spec_lst))[0]
        assert filter_vspec.value =="Boat"
def test_custom_plot_setting():
    def change_color_make_transparent_add_title(chart):
        chart = chart.configure_mark(color="green",opacity=0.2)
        chart.title = "Test Title"
        return chart
    df = pd.read_csv("lux/data/car.csv")
    df.set_plot_config(change_color_make_transparent_add_title)
    df.show_more()
    config_mark_addition = 'chart = chart.configure_mark(color="green",opacity=0.2)'
    title_addition ='chart.title = "Test Title"'
    exported_code_str = df.recommendation["Correlation"][0].to_Altair()
    assert config_mark_addition in exported_code_str
    assert title_addition in exported_code_str

def test_remove():
    from lux.vis.Vis import Vis
    df = pd.read_csv("lux/data/car.csv")
    view = Vis([lux.VisSpec("Horsepower"),lux.VisSpec("Acceleration")],df)
    view.remove_column_from_spec("Horsepower",remove_first=False)
    assert view.spec_lst[0].attribute == "Acceleration"
def test_remove_identity():
    from lux.vis.Vis import Vis
    df = pd.read_csv("lux/data/car.csv")
    view = Vis(["Horsepower","Horsepower"],df)
    view.remove_column_from_spec("Horsepower")
    assert (view.spec_lst == []),"Remove all instances of Horsepower"

    df = pd.read_csv("lux/data/car.csv")
    view = Vis(["Horsepower","Horsepower"],df)
    view.remove_column_from_spec("Horsepower",remove_first=True)
    assert (len(view.spec_lst)==1),"Remove only 1 instances of Horsepower"
    assert (view.spec_lst[0].attribute=="Horsepower"),"Remove only 1 instances of Horsepower"
def test_refresh_collection():
    df = pd.read_csv("lux/data/car.csv")
    df.set_context([lux.VisSpec(attribute = "Acceleration"),lux.VisSpec(attribute = "Horsepower")])
    df.show_more()
    enhanceCollection = df.recommendation["Enhance"]
    enhanceCollection.refresh_data(df[df["Origin"]=="USA"])
    