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


class Event:
    """
    Event represents a single operation applied to the dataframe, with input arguments of operation recorded
    """

    def __init__(self, op_name, cols, ex_count, *args, **kwargs):
        if type(cols) != list:
            cols = [cols]

        self.op_name = op_name
        self.cols = cols
        self.ex_count = ex_count
        self.args = args
        self.kwargs = kwargs

    def copy(self):
        event_copy = Event(self.op_name, self.cols, self.ex_count, *self.args, **self.kwargs)

        return event_copy

    def __repr__(self):
        s = f"<Event (id: {id(self)}) @[{self.ex_count}]: \033[1m{self.op_name}\033[0m"
        if self.cols:
            s += f", cols={self.cols}"
        if self.args != () or self.kwargs != {}:
            s += f", args={self.args}, kwargs={self.kwargs.keys()}"
        s += ">"
        return s

    def to_JSON(self):
        returned_new_df = self.kwargs.get("rank_type", None) == "parent"

        return {
            "op_name": self.op_name,
            "cols": self.cols,
            "ex_count": self.ex_count,
            "ret_new_df": returned_new_df,
        }
