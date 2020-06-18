from .context import lux
import pytest
import pandas as pd

def test_viewCollection():
    df = pd.read_csv("lux/data/olympic.csv")
    from lux.view.ViewCollection import ViewCollection
    vc = ViewCollection(["Height","SportType=Ball","?"])
    vc = vc.load(df)
    viewWithYear = list(filter(lambda x: x.getAttrByAttrName("Year")!=[],vc))[0]
    assert viewWithYear.getAttrByChannel("x")[0].attribute=="Year"
    assert len(vc) == len(df.columns) -1 -1 #remove 1 for view with same filter attribute and remove 1 view with for same attribute
    vc = ViewCollection(["Height","?"])
    vc = vc.load(df)
    assert len(vc) == len(df.columns) -1 #remove 1 for view with for same attribute

def test_customPlotSetting():
    def changeColorMakeTransparentAddTitle(chart):
        chart = chart.configure_mark(color="green",opacity=0.2)
        chart.title = "Test Title"
        return chart
    df = pd.read_csv("lux/data/car.csv")
    df.setPlotConfig(changeColorMakeTransparentAddTitle)
    df.showMore()
    configMarkAddition = 'chart = chart.configure_mark(color="green",opacity=0.2)'
    titleAddition ='chart.title = "Test Title"'
    exportedCodeStr = df.recommendation["Correlation"][0].toAltair()
    assert configMarkAddition in exportedCodeStr
    assert titleAddition in exportedCodeStr
