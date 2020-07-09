from .context import lux
import pytest
import pandas as pd

def test_view_collection():
    df = pd.read_csv("lux/data/olympic.csv")
    from lux.view.ViewCollection import ViewCollection
    vc = ViewCollection(["Height","SportType=Ball","?"])
    vc = vc.load(df)
    view_with_year = list(filter(lambda x: x.get_attr_by_attr_name("Year")!=[],vc))[0]
    assert view_with_year.get_attr_by_channel("x")[0].attribute=="Year"
    assert len(vc) == len(df.columns) -1 -1 #remove 1 for view with same filter attribute and remove 1 view with for same attribute
    vc = ViewCollection(["Height","?"])
    vc = vc.load(df)
    assert len(vc) == len(df.columns) -1 #remove 1 for view with for same attribute

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
