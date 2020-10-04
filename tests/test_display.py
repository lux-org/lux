#  Copyright 2019-2020 The Lux Authors.
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from .context import lux
import pytest
import pandas as pd
from lux.vis.Vis import Vis
from lux.vis.VisList import VisList
def test_to_pandas():
    df = pd.read_csv("lux/data/car.csv")
    df.to_pandas()

def test_display_LuxDataframe():
    df = pd.read_csv("lux/data/car.csv")
    df._repr_html_()
    
def test_display_Vis():
    df = pd.read_csv("lux/data/car.csv")
    vis = Vis(["Horsepower","Acceleration"],df)
    vis._repr_html_()
    
def test_display_VisList():
    df = pd.read_csv("lux/data/car.csv")
    vislist = VisList(["?","Acceleration"],df)
    vislist._repr_html_()