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

import pandas as pd
from .frame import LuxDataFrame

global originalDF
# Keep variable scope of original pandas df
originalDF = pd.core.frame.DataFrame


def setOption(overridePandas=True):
    if overridePandas:
        pd.DataFrame = (
            pd.io.json._json.DataFrame
        ) = pd.io.parsers.DataFrame = pd.core.frame.DataFrame = LuxDataFrame
    else:
        pd.DataFrame = pd.io.parsers.DataFrame = pd.core.frame.DataFrame = originalDF


setOption(overridePandas=True)
