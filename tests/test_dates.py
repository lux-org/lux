from .context import lux
import pytest
import pandas as pd
import numpy as np
from lux.utils import date_utils

def test_dateformatter():
    ldf = pd.read_csv("lux/data/car.csv")
    ldf["Year"] = pd.to_datetime(ldf["Year"], format='%Y')  # change pandas dtype for the column "Year" to datetype
    timestamp = np.datetime64('2019-08-26')

    assert(date_utils.dateFormatter(timestamp,ldf) == '2019')

    ldf["Year"][0] = np.datetime64('1970-03-01') # make month non unique

    assert (date_utils.dateFormatter(timestamp, ldf) == '2019-8')


    ldf["Year"][0] = np.datetime64('1970-03-03') # make day non unique

    assert (date_utils.dateFormatter(timestamp, ldf) == '2019-8-26')