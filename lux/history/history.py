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

from typing import List, Union, Callable, Dict
from lux.history.event import Event


class History:
    """
    History maintains a list of past Pandas operations performed on the dataframe
    Currently only supports custom overridden functions (head, tail, info, describe)
    """

    def __init__(self):
        self._events = []

    def __getitem__(self, key):
        return self._events[key]

    def __setitem__(self, key, value):
        self._events[key] = value

    def __len__(self):
        return len(self._events)

    def __repr__(self):
        event_repr = []
        for event in self._events:
            event_repr.append(event.__repr__())
        return "[" + "\n".join(event_repr) + "]"

    def append_event(self, name, *args, **kwargs):
        event = Event(name, *args, **kwargs)
        self._events.append(event)

    def copy(self):
        history_copy = History()
        history_copy._events.extend(self._events)
        return history_copy
