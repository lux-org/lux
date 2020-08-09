from scipy.stats import kurtosis
from typing import List
import pandas as pd
import math
def kurtosisScore(data, interestVar:str = "", filterVar:str = "", filterVal:str = ""):
    if filterVar == "":
        return(kurtosis(data[interestVar]))
    else:
        filteredData = data[data[filterVar] == filterVal]
        filteredSize = filteredData.shape[0]
        dataSize = data.shape[0]

        output = 0.1*(filteredSize/dataSize)*math.pow(kurtosis(filteredData[interestVar])-kurtosis(data[interestVar]), 2)
        return(output)
