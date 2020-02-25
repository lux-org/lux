import pandas as pd
from .LuxDataframe import LuxDataFrame
global originalDF;
# Keep variable scope of original pandas df
originalDF = pd.core.frame.DataFrame

def delegate(bool):
    if bool:
        pd.DataFrame = pd.io.parsers.DataFrame = pd.core.frame.DataFrame = LuxDataFrame
    else:
        pd.DataFrame = pd.io.parsers.DataFrame = pd.core.frame.DataFrame = originalDF

delegate(True)