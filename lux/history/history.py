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
from IPython import get_ipython
import lux
import warnings

from IPython.core.debugger import set_trace

class History:
    """
    History maintains a list of past Pandas operations performed on the dataframe
    Currently only supports custom overridden functions (head, tail, info, describe)
    """

    def __init__(self, ldf):
        self._events = []
        self._frozen_count = 0
        self._time_decay = .9
        self.parent_ldf = ldf
        self.kernel = get_ipython()

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

    # deep copy 
    def copy(self):
        history_copy = History(self.parent_ldf)
        _events_copy = [item.copy() for item in self._events]
        history_copy._events = _events_copy
        #history_copy._events.extend(self._events) # NOTE if events become mutable they need to be copied too 
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

        if self._frozen_count < 0:
            warnings.warn(
                "History was unfrozen without an associted freeze and thus may be corrupted.",
                stacklevel=2,
            )

    def append_event(self, op_name, cols, *args, **kwargs):
        if self._frozen_count == 0:
            event = Event(op_name, cols, 1, self.kernel.execution_count, *args, **kwargs)
            self.decay_weights()
            self._events.append(event)
            # aggressively refresh actions 
            lux.config.update_actions["flag"] = True
    
    def decay_weights(self):
        for e in self._events:
            e.weight *= self._time_decay
    
    def filter_by_ex_time(self, t):
        return list(filter(lambda x: x.ex_count == t, self._events))
            
    ######################
    ## Implicit Intent  ##
    ######################

    def get_implicit_intent(self, valid_cols, col_thresh = .25):
        """
        Iterates through history events and gets ordering of columns by user interest 
        and most recent signal.

        Parameters
        ----------
            valid_cols: Iterable like list or Index
                Columns that are in the df we want the intent for. Filter out cols not in this list
            
            col_thresh: float
                Events with weight less than this threshold are not included
        
        Returns
        -------
            mre: Event 
                most recent non column reference event 
            
            val_col_order: list 
                ordered list of important columns (descending order) or empty list
        """
        mre = None
        agg_col_ref = {}
        col_order = []

        if self._events:
            for e in self._events[::-1]: # reverse iterate
                
                # filter out decayed history
                if e.weight >= col_thresh:
                    
                    # first event that is not just col ref is most recent for vis
                    if not mre and e.op_name != "col_ref":
                        mre = e 
                        continue
                    
                    for c in e.cols:
                        if c in agg_col_ref:
                            agg_col_ref[c] += e.weight 
                        else:
                            agg_col_ref[c] = e.weight
            
            # get sorted column order by aggregate weight, thresholded 
            col_order = list(agg_col_ref.items())
            col_order.sort(key=lambda x: x[1], reverse=True)
            col_order = [i[0] for i in col_order]
        
        # validate the returned signals
        #parent_cols = self.parent_ldf.columns
        val_col_order = [item for item in col_order if item in valid_cols]
        if mre:
            val_mre_cols = [item for item in mre.cols if item in valid_cols]
            val_mre = mre.copy()
            val_mre.cols = val_mre_cols
            mre = val_mre
        
        return mre, val_col_order