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

# Register the commonly used modules (similar to how pandas does it: https://github.com/pandas-dev/pandas/blob/master/pandas/__init__.py)
from lux.vis.Clause import Clause
from lux.core.frame import LuxDataFrame
from lux.core.sqltable import LuxSQLTable
from ._version import __version__, version_info
from lux._config import config
from lux._config.config import warning_format

from lux._config import Config

config = Config()

from lux.action.default import register_default_actions

register_default_actions()
