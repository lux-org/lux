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
import collections
import warnings

import lux


class Ordering:
    @staticmethod
    def interestingness(collection, desc):
        collection.sort(key=lambda x: x.score, reverse=desc)

    @staticmethod
    def title(collection, desc):
        collection.sort(key=lambda x: x.title, reverse=desc)

    @staticmethod
    def x_alpha(collection, desc):
        collection.sort(key=lambda x: x.get_attr_by_channel("x")[0].attribute, reverse=desc)

    @staticmethod
    def y_alpha(collection, desc):
        collection.sort(key=lambda x: x.get_attr_by_channel("y")[0].attribute, reverse=desc)


def resolve_value(value):
    if type(value) is str:
        if value == "interestingness":
            return Ordering.interestingness
        elif value == "alphabetical_by_title":
            return Ordering.title
        elif value == "alphabetical_by_x":
            return Ordering.x_alpha
        elif value == "alphabetical_by_y":
            return Ordering.y_alpha
    else:
        assert callable(value), "You must pass in a default string or a custom function."
        return value


class OrderingDict(collections.MutableMapping, dict):
    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        if key in lux.config.actions or key == "global":
            dict.__setitem__(self, key, resolve_value(value))
        else:
            warnings.warn(
                f"Key is not a valid action; must be one of the following: {self.actions.keys()}.",
                stacklevel=2,
            )

    def __delitem__(self, key):
        dict.__delitem__(self, key)

    def __iter__(self):
        return dict.__iter__(self)

    def __len__(self):
        return dict.__len__(self)

    def __contains__(self, x):
        return dict.__contains__(self, x)
