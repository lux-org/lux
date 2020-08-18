import pandas as pd
from .frame import LuxDataFrame
global originalDF;
# Keep variable scope of original pandas df
originalDF = pd.core.frame.DataFrame

def setOption(overridePandas=True):
    if (overridePandas):
        pd.DataFrame = pd.io.parsers.DataFrame = pd.core.frame.DataFrame = LuxDataFrame
    else:
        pd.DataFrame = pd.io.parsers.DataFrame = pd.core.frame.DataFrame = originalDF

setOption(overridePandas=True)