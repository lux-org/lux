import traceback
import typing as tp
import warnings
from copy import copy, deepcopy

import pandas as pd
import numpy as np

import lux
from lux.core.frame import LuxDataFrame, LuxDataFrameMethods
from lux.core.series import LuxSeries, LuxSeriesMethods
from lux.utils.utils import patch

DataFrame = pd.DataFrame
Series = pd.Series
DataFrame = tp.cast(tp.Type[LuxDataFrame], DataFrame)
Series = tp.cast(tp.Type[LuxSeries], Series)


# MUST register here for new properties!!
DataFrame._metadata.append("_LUX_")


@patch(DataFrame, name="lux")
@property
def _lux(self: LuxDataFrame) -> "LuxDataFrameMethods":
    return self._LUX_


@patch(DataFrame)
def __init__(self: LuxDataFrame, *args, **kwargs):
    self._super__init__(*args, **kwargs)
    self._LUX_ = LuxDataFrameMethods(self)


# @patch(DataFrame)
# @property
# def _constructor(self: LuxDataFrame):
#     def _construct_and_copy(*args, **kwargs) -> DataFrame:
#         df = self._super_constructor(*args, **kwargs)

#         # copies the accessor and sets the new dataframe
#         df._LUX_ = copy(self.lux)  # try deepcopy?
#         df._LUX_.df = df

#         return df

#     return _construct_and_copy


@patch(DataFrame)
@property
def _constructor_sliced(self: LuxDataFrame):
    def _create_and_copy(*args, **kwargs):
        series = Series(*args, **kwargs)
        series._LUX_ = LuxSeriesMethods.from_lux_object(
            "series", series, self.lux)

        return series

    return _create_and_copy


@patch(DataFrame, name="copy")
def _copy(self: LuxDataFrame, *args, **kwargs):
    df = self._super_copy(*args, **kwargs)
    df._LUX_ = copy(self.lux)
    # df._LUX_ = deepcopy(self.lux)
    return df


@patch(DataFrame)
def __getattr__(self: LuxDataFrame, name):
    ret_value = self._super__getattr__(name)
    self.lux.expire_metadata()
    self.lux.expire_recs()
    return ret_value


@patch(DataFrame)
def __setattr__(self: LuxDataFrame, key, value):
    # this method is not strictly necessary, but debugging during testing fails without it
    self.__dict__[key] = value


@patch(DataFrame)
def _set_axis(self: LuxDataFrame, axis, labels):
    self._super_set_axis(axis, labels)
    self.lux.expire_metadata()
    self.lux.expire_recs()


@patch(DataFrame)
def _update_inplace(self: LuxDataFrame, *args, **kwargs):
    self._super_update_inplace(*args, **kwargs)
    self.lux.expire_metadata()
    self.lux.expire_recs()


@patch(DataFrame)
def _set_item(self: LuxDataFrame, key, value):
    self._super_set_item(key, value)
    self.lux.expire_metadata()
    self.lux.expire_recs()


@patch(DataFrame)
def _ipython_display_(self: LuxDataFrame):
    import ipywidgets as widgets
    from IPython.display import clear_output, display

    try:
        if self.lux._pandas_only:
            display(self.lux.display_pandas())
            self.lux._pandas_only = False
        else:
            if not self.index.nlevels >= 2 or self.columns.nlevels >= 2:
                self.lux.maintain_metadata()

                if self.lux._intent != [] and (not hasattr(self.lux, "_compiled") or not self.lux._compiled):
                    from lux.processor.Compiler import Compiler

                    self.current_vis = Compiler.compile_intent(
                        self, self.lux._intent)

            if lux.config.default_display == "lux":
                self.lux._toggle_pandas_display = False
            else:
                self.lux._toggle_pandas_display = True

            # df_to_display.maintain_recs() # compute the recommendations (TODO: This can be rendered in another thread in the background to populate self.lux._widget)
            self.lux.maintain_recs()

            # Observers(callback_function, listen_to_this_variable)
            self.lux._widget.observe(
                self.lux.remove_deleted_recs, names="deletedIndices")
            self.lux._widget.observe(
                self.lux.set_intent_on_click, names="selectedIntentIndex")

            button = widgets.Button(
                description="Toggle Pandas/Lux",
                layout=widgets.Layout(width="140px", top="5px"),
            )
            self.lux.output = widgets.Output()
            display(button, self.lux.output)

            def on_button_clicked(b):
                with self.lux.output:
                    if b:
                        self.lux._toggle_pandas_display = not self.lux._toggle_pandas_display
                    clear_output()
                    if self.lux._toggle_pandas_display:
                        display(self.lux.display_pandas())
                    else:
                        # b.layout.display = "none"
                        display(self.lux._widget)
                        # b.layout.display = "inline-block"

            button.on_click(on_button_clicked)
            on_button_clicked(None)

    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        if lux.config.pandas_fallback:
            warnings.warn(
                "\nUnexpected error in rendering Lux widget and recommendations. "
                "Falling back to Pandas display.\n"
                "Please report the following issue on Github: https://github.com/lux-org/lux/issues \n",
                stacklevel=2,
            )
            warnings.warn(traceback.format_exc())
            display(self.lux.display_pandas())
        else:
            raise


@patch(DataFrame)
def head(self: LuxDataFrame, n: int = 5):
    ret_val = self._super_head(n)
    ret_val._prev = self
    ret_val._history.append_event("head", n=5)
    return ret_val


@patch(DataFrame)
def tail(self: LuxDataFrame, n: int = 5):
    ret_val = self._super_tail(n)
    ret_val._prev = self
    ret_val._history.append_event("tail", n=5)
    return ret_val


@patch(DataFrame)
def groupby(self: LuxDataFrame, *args, **kwargs):
    history_flag = False
    if "history" not in kwargs or ("history" in kwargs and kwargs["history"]):
        history_flag = True
    if "history" in kwargs:
        del kwargs["history"]
    groupby_obj = self._super_groupby(*args, **kwargs)
    for attr in self._metadata:
        groupby_obj.__dict__[attr] = getattr(self, attr, None)
    if history_flag:
        groupby_obj._history = groupby_obj._history.copy()
        groupby_obj._history.append_event("groupby", *args, **kwargs)
    groupby_obj.pre_aggregated = True
    return groupby_obj
