from .context import lux
import pytest
import pandas as pd

def test_vis():
    df = pd.read_csv("lux/data/olympic.csv")
    from lux.vis.Vis import Vis
    vis = Vis(["Height","SportType=Ball"],df)
    assert vis.get_attr_by_attr_name("Height")[0].bin_size!=0
    assert vis.get_attr_by_attr_name("Record")[0].aggregation == 'count'
    
def test_vis_set_specs():
    df = pd.read_csv("lux/data/olympic.csv")
    from lux.vis.Vis import Vis
    vis = Vis(["Height","SportType=Ball"],df)
    vis.set_query(["Height","SportType=Ice"])
    assert vis.get_attr_by_attr_name("SportType")[0].value =="Ice"

def test_vis_collection():
    df = pd.read_csv("lux/data/olympic.csv")
    from lux.vis.VisCollection import VisCollection
    vc = VisCollection(["Height","SportType=Ball","?"],df)
    vis_with_year = list(filter(lambda x: x.get_attr_by_attr_name("Year")!=[],vc))[0]
    assert vis_with_year.get_attr_by_channel("x")[0].attribute=="Year"
    assert len(vc) == len(df.columns) -1 -1 #remove 1 for vis with same filter attribute and remove 1 vis with for same attribute
    vc = VisCollection(["Height","?"],df)
    assert len(vc) == len(df.columns) -1 #remove 1 for vis with for same attribute

def test_vis_collection_set_query():
    df = pd.read_csv("lux/data/olympic.csv")
    from lux.vis.VisCollection import VisCollection
    vc = VisCollection(["Height","SportType=Ice","?"],df)
    vc.set_query(["Height","SportType=Boat","?"])
    for v in vc.collection: 
        filter_vspec = list(filter(lambda x: x.channel=="",v._inferred_query))[0]
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
    vis = Vis([lux.VisSpec("Horsepower"),lux.VisSpec("Acceleration")],df)
    vis.remove_column_from_spec("Horsepower",remove_first=False)
    assert vis._inferred_query[0].attribute == "Acceleration"
def test_remove_identity():
    from lux.vis.Vis import Vis
    df = pd.read_csv("lux/data/car.csv")
    vis = Vis(["Horsepower","Horsepower"],df)
    vis.remove_column_from_spec("Horsepower")
    assert (vis._inferred_query == []),"Remove all instances of Horsepower"

    df = pd.read_csv("lux/data/car.csv")
    vis = Vis(["Horsepower","Horsepower"],df)
    vis.remove_column_from_spec("Horsepower",remove_first=True)
    assert (len(vis._inferred_query)==1),"Remove only 1 instances of Horsepower"
    assert (vis._inferred_query[0].attribute=="Horsepower"),"Remove only 1 instances of Horsepower"
def test_refresh_collection():
    df = pd.read_csv("lux/data/car.csv")
    df.set_context([lux.VisSpec(attribute = "Acceleration"),lux.VisSpec(attribute = "Horsepower")])
    df.show_more()
    enhanceCollection = df.recommendation["Enhance"]
    enhanceCollection.refresh_source(df[df["Origin"]=="USA"])

def test_vis_custom_aggregation_as_str():
    df = pd.read_csv("lux/data/college.csv")
    from lux.vis.Vis import Vis
    import numpy as np
    vis = Vis(["HighestDegree",lux.VisSpec("AverageCost",aggregation="max")],df)
    assert vis.get_attr_by_data_model("measure")[0].aggregation == "max"
    assert vis.get_attr_by_data_model("measure")[0]._aggregation_name =='max'    
    
def test_vis_custom_aggregation_as_numpy_func():
    df = pd.read_csv("lux/data/college.csv")
    from lux.vis.Vis import Vis
    import numpy as np
    vis = Vis(["HighestDegree",lux.VisSpec("AverageCost",aggregation=np.ptp)],df)
    assert vis.get_attr_by_data_model("measure")[0].aggregation == np.ptp
    assert vis.get_attr_by_data_model("measure")[0]._aggregation_name =='ptp'