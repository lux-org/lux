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
import numpy as np
from contextlib import contextmanager

from IPython.core.debugger import set_trace


class History:
    """
    History maintains a list of past Pandas operations performed on the dataframe
    Currently only supports custom overridden functions (head, tail, info, describe)
    """

    def __init__(self, ldf):
        self._events = []
        self._frozen_count = 0
        self._time_decay = 0.9
        self.parent_ldf = ldf
        self.kernel = get_ipython()
        self.col_thresh = 0.25

        self.selectedItemIdx = None

        # class variable TODO is there better way for this to be stored
        self.base_weights = {"value_counts": 1, "col_ref": 0.5, "assign": 2}

    def __getitem__(self, key):
        return self._events[key]

    def get_hist_item(self, key, valid_cols):
        e = self._events[key]

        return self.validate_mre(e, valid_cols)

    def __setitem__(self, key, value):
        if self._frozen_count == 0:
            self._events[key] = value

    def __len__(self):
        return len(self._events)

    def __repr__(self):
        event_repr = []
        weights = self.get_weights()
        for event, weight in zip(self._events, weights):
            event_repr.append(f"{event.__repr__()} with weight {weight}")
        return "[\n" + ",\n".join(event_repr) + "\n]"

    def to_JSON(self):
        _events_json = []

        for i, e in enumerate(self._events):
            js = {**e.to_JSON(), "og_index": i}
            _events_json.append(js)

        return _events_json

    # deep copy
    def copy(self):
        history_copy = History(self.parent_ldf)
        _events_copy = [item.copy() for item in self._events]
        history_copy._events = _events_copy
        return history_copy

    @contextmanager
    def pause(self):
        """
        Supports with notation to freeze history. For example...

        with df.history.pause():
            # anything executed here not logged to history
        """
        self.freeze()
        try:
            yield self
        finally:
            self.unfreeze()

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

    def clear(self):
        if self._frozen_count == 0:
            self._events = []
            return True

        return False

    def delete_at(self, index):
        try:
            if self._frozen_count == 0:
                item = self._events.pop(index)
                return item

            return None
        except IndexError:
            return None

    def append_event(self, op_name, cols, *args, **kwargs):
        if self._frozen_count == 0:
            event = Event(op_name, cols, self.kernel.execution_count, *args, **kwargs)
            self._events.append(event)
            # aggressively refresh actions
            lux.config.update_actions["flag"] = True
            # TODO change this to use df._recs_fresh -- does it make a difference?

    def get_weights(self, event_list=None):
        """
        Calculate the weights for each event in the history
        """
        if not event_list:
            event_list = self._events

        n_events = len(event_list)
        weight_arr = np.zeros(n_events)

        ex_decay = 0.85  # how much to decay between ex [n] to [n - 1]
        cell_decay = 0.95  # how much to decay between lines in ex cell [n]

        curr_ex = -1
        rolling_ex_decay = 1
        rolling_cell_decay = 1

        for i in range(n_events - 1, -1, -1):  # reverse iterate
            e = event_list[i]
            base_w = self.base_weights.get(e.op_name, 1)

            if e.ex_count != curr_ex:
                if curr_ex != -1:  # dont decay first event
                    rolling_ex_decay *= ex_decay

                curr_ex = e.ex_count
                rolling_cell_decay = 1
            else:
                rolling_cell_decay *= cell_decay

            w = base_w * rolling_ex_decay * rolling_cell_decay

            weight_arr[i] = w

        return list(weight_arr)

    def edit_event(self, edit_index, new_op_name, new_cols, *args, **kwargs):
        """
        Attempt to edit event at index edit_index.
        Returns T/F if edit succeeded
        """
        if self._frozen_count == 0:
            try:
                e = self._events[edit_index]
                e.op_name = new_op_name
                e.cols = new_cols
                e.args = args
                e.kwargs = kwargs

                return True
            except IndexError:
                return False
        return False

    def check_event(self, event_index, **kwargs):
        """
        See if event at event_index has equal properties provided as kwargs
        Note:
            If an arg is provided as None and is not in Event this will still return True
            e.g. check_event(0, fake_arg=None) will return true (if event at 0)
        Returns truthiness of comp
        """
        try:
            e = self._events[event_index]
            for k, v in kwargs.items():
                e_v = getattr(e, k, None)
                if e_v != v:
                    return False

            return True
        except IndexError:
            return False

    def filter_by_ex_time(self, t):
        return list(filter(lambda x: x.ex_count == t, self._events))

    ######################
    ## Implicit Intent  ##
    ######################

    def get_cleaned_events(self):
        """
        get self.events that are NOT parent events,
        only care about those that actually happened to this df
        """
        cleaned_e = []

        for e in self._events:
            if e.kwargs.get("rank_type", None) != "parent":
                cleaned_e.append(e)

        return cleaned_e

    def get_implicit_intent(self, valid_cols):
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
        agg_col_ref = {}
        col_order = []

        weights = self.get_weights()

        if self._events:
            for i in range(len(self._events) - 1, -1, -1):
                e = self._events[i]
                w = weights[i]

                # filter out decayed history
                if w >= self.col_thresh:
                    # include col ref even if for returned child df
                    for c in e.cols:
                        if c in agg_col_ref:
                            agg_col_ref[c] += w
                        else:
                            agg_col_ref[c] = w

            # get sorted column order by aggregate weight, thresholded
            col_order = list(agg_col_ref.items())
            col_order.sort(key=lambda x: x[1], reverse=True)
            col_order = [i[0] for i in col_order]

        # validate the returned signals
        val_col_order = [item for item in col_order if item in valid_cols]

        return val_col_order

    def get_mre(self, valid_cols):
        mre = None
        weights = self.get_weights()
        i = len(self._events) - 1

        while i >= 0 and not mre:
            e = self._events[i]
            w = weights[i]

            if w >= self.col_thresh and (e.kwargs.get("rank_type", None) != "parent") and not mre:
                mre = e
                break
            i -= 1

        mre = self.validate_mre(mre, valid_cols)

        return mre, i

    def validate_mre(self, mre, valid_cols):
        if mre:
            val_mre_cols = [item for item in mre.cols if item in valid_cols]
            val_mre = mre.copy()
            val_mre.cols = val_mre_cols
            mre = val_mre

        return mre
