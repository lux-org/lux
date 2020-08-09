from scipy.stats import skew
from typing import List
import pandas as pd
import math
def skewScore(measure, data, filterVar:str = "", filterVal:str = ""):
    if filterVar == "":
        return(skew(data[measure]))
    else:
        filteredData = data[data[measure] == filterVal]
        filteredSize = filteredData.shape[0]
        dataSize = data.shape[0]

        output = 0.1*(filteredSize/dataSize)*math.pow(skew(filteredData[measure])-skew(data[measure]),2)
        return(output)
