from .context import lux
import pytest
import pandas as pd

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