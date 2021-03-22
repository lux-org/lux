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

# CodeHistoryItem = namedtuple("CodeHistoryItem", "cols f_name f_arg_dict ex_order code_str")

class Event:
    """
    Event represents a single operation applied to the dataframe, with input arguments of operation recorded
    """

    def __init__(self, op_name, cols, weight, ex_count, *args, **kwargs):
        if type(cols) != list:
            cols = [cols]
        
        self.op_name = op_name
        self.cols = cols
        self.weight = weight
        self.ex_count = ex_count
        self.args = args
        self.kwargs = kwargs
    
    def copy(self):
        event_copy = Event(self.op_name, 
                            self.cols, 
                            self.weight,
                            self.ex_count,
                            *self.args,
                            **self.kwargs)
        
        return event_copy

    def __repr__(self):
        s = f"<Event({id(self)}): {self.op_name}, weight: {self.weight}, ex_count: {self.ex_count}"
        if self.cols:
            s += f", cols={self.cols}"
        if self.args != () or self.kwargs != {}:
            s += f", args={self.args}, kwargs={self.kwargs}"
        s += ">"
        return s
