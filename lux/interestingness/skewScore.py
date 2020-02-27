from scipy.stats import skew
from typing import List
import pandas as pd
import math
def skewScore(data, interestVar:str = "", filterVar:str = "", filterVal:str = ""):
    if filterVar == "":
        return(skew(data[interestVar]))
    else:
        filteredData = data[data[filterVar] == filterVal]
        filteredSize = filteredData.shape[0]
        dataSize = data.shape[0]

        output = 0.1*(filteredSize/dataSize)*math.pow(skew(filteredData[interestVar])-skew(data[interestVar]),2)
        return(output)
