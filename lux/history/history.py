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

    def __init__(self, ldf):
        self._events = []
        self._frozen_count = 0
        self._ex_count = 0
        self._time_decay = .9
        self.parent_ldf = ldf

    def __getitem__(self, key):
        return self._events[key]

    def __setitem__(self, key, value):
        if self._frozen_count == 0:
            self._events[key] = value

    def __len__(self):
        return len(self._events)

    def __repr__(self):
        event_repr = []
        for event in self._events:
            event_repr.append(event.__repr__())
        return "[" + ",\n".join(event_repr) + "]"

    def copy(self):
        history_copy = History()
        history_copy._events.extend(self._events)
        return history_copy

    ######################
    ## State management ##
    ######################

    # freeze/unfreeze offer locks on adding new 
    # info to the history so we dont log internal calls
    def freeze(self):
        self._frozen_count += 1 
    
    def unfreeze(self):
        self._frozen_count -= 1 

    def append_event(self, op_name, cols, *args, **kwargs):
        if self._frozen_count == 0:
            event = Event(op_name, cols, 1, self._ex_count, *args, **kwargs)
            self.decay_weights()
            self._events.append(event)
            self._ex_count += 1
    
    def decay_weights(self):
        for e in self._events:
            e.weight *= self._time_decay
            
    ######################
    ## Implicit Intent  ##
    ######################

    def get_implicit_intent(self, valid_cols, col_thresh = .25):
        """
        Iterates through history events and gets ordering of columns by user interest 
        and most recent signal.
        """
        most_recent_signal = None
        agg_col_ref = {}
        col_order = []

        if self._events:
            for e in self._events[::-1]: # reverse iterate
                
                # first event that is not just col ref is most recent for vis
                if not most_recent_signal and e.op_name != "col_ref":
                    most_recent_signal = e 
                
                for c in e.cols:
                    if c in agg_col_ref:
                        agg_col_ref[c] += e.weight 
                    else:
                        agg_col_ref[c] = e.weight
            
            # get sorted column order by aggregate weight, thresholded 
            col_order = list(agg_col_ref.items())
            col_order.sort(key=lambda x: x[1], reverse=True)
            col_order = [i[0] for i in col_order if i[1] > col_thresh]
        
        # validate the returned signals
        #parent_cols = self.parent_ldf.columns
        val_col_order = [item for item in col_order if item in valid_cols]
        if most_recent_signal:
            mre_cols = [item for item in most_recent_signal.cols if item in valid_cols]
            most_recent_signal.cols = mre_cols
        
        return most_recent_signal, val_col_order