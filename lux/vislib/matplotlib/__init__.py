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

from lux.utils.utils import matplotlib_setup
import matplotlib.pyplot as plt

plt.rcParams.update({"figure.max_open_warning": 0})
plt.rcParams.update(
    {
        "axes.titlesize": 15,
        "axes.titleweight": "bold",
        "axes.labelweight": "bold",
        "axes.labelsize": 13,
        "legend.fontsize": 13,
        "legend.title_fontsize": 13,
        "xtick.labelsize": 13,
        "ytick.labelsize": 13,
    }
)
