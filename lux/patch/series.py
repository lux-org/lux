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


@patch(Series, name="lux")
@property
def _lux(self: LuxSeries) -> "LuxSeriesMethods":
    return self._LUX_


@patch(Series)
def __init__(self: LuxSeries, *args, **kwargs):
    self._super__init__(*args, **kwargs)
    self._LUX_ = LuxSeriesMethods(self)


@patch(Series)
@property
def _constructor(self: LuxSeries):
    def _construct_and_copy(*args, **kwargs) -> DataFrame:
        series = self._super_constructor(*args, **kwargs)

        # copies the accessor and sets the new dataframe
        series._LUX_ = copy(self.lux)  # try deepcopy?
        series._LUX_.series = series

        return series

    return _construct_and_copy


@patch(Series)
@property
def _constructor_expanddim(self: LuxSeries):
    def _construct_and_copy(*args, **kwargs):
        df = DataFrame(*args, **kwargs)
        df._LUX_ = LuxDataFrameMethods.from_lux_object("df", df, self.lux)
        return df

    _construct_and_copy._get_axis_number = DataFrame._get_axis_number

    return _construct_and_copy


@patch(Series, name="copy")
def _copy(self: LuxSeries, *args, **kwargs):
    series = self._super_copy(*args, **kwargs)
    series._LUX_ = copy(self.lux)
    return series


@patch(Series)
def _ipython_display_(self):
    from IPython.display import display
    from IPython.display import clear_output
    import ipywidgets as widgets

    series_repr = super(LuxSeries, self).__repr__()

    ldf = DataFrame(self)

    # Default column name 0 causes errors
    if self.name is None:
        ldf = ldf.rename(columns={0: " "})
    self._ldf = ldf

    try:
        # Ignore recommendations when Series a results of:
        # 1) Values of the series are of dtype objects (df.dtypes)
        is_dtype_series = (
            all(isinstance(val, np.dtype)
                for val in self.values) and len(self.values) != 0
        )
        # 2) Mixed type, often a result of a "row" acting as a series (df.iterrows, df.iloc[0])
        # Tolerant for NaNs + 1 type
        mixed_dtype = len(set([type(val) for val in self.values])) > 2
        if ldf.lux._pandas_only or is_dtype_series or mixed_dtype:
            print(series_repr)
            ldf.lux._pandas_only = False
        else:
            if not self.index.nlevels >= 2:
                ldf.lux.maintain_metadata()

            if lux.config.default_display == "lux":
                self.lux._toggle_pandas_display = False
            else:
                self.lux._toggle_pandas_display = True

            # df_to_display.maintain_recs() # compute the recommendations (TODO: This can be rendered in another thread in the background to populate self._widget)
            ldf.lux.maintain_recs(is_series="Series")

            # Observers(callback_function, listen_to_this_variable)
            ldf.lux._widget.observe(ldf.lux.remove_deleted_recs,
                                    names="deletedIndices")
            ldf.lux._widget.observe(ldf.lux.set_intent_on_click,
                                    names="selectedIntentIndex")

            self._widget = ldf.lux._widget
            self._recommendation = ldf.lux._recommendation

            # box = widgets.Box(layout=widgets.Layout(display='inline'))
            button = widgets.Button(
                description="Toggle Pandas/Lux",
                layout=widgets.Layout(width="140px", top="5px"),
            )
            ldf.output = widgets.Output()
            # box.children = [button,output]
            # output.children = [button]
            # display(box)
            display(button, ldf.output)

            def on_button_clicked(b):
                with ldf.output:
                    if b:
                        self.lux._toggle_pandas_display = not self.lux._toggle_pandas_display
                    clear_output()
                    if self.lux._toggle_pandas_display:
                        print(series_repr)
                    else:
                        # b.layout.display = "none"
                        display(ldf.lux._widget)
                        # b.layout.display = "inline-block"

            button.on_click(on_button_clicked)
            on_button_clicked(None)

    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        warnings.warn(
            "\nUnexpected error in rendering Lux widget and recommendations. "
            "Falling back to Pandas display.\n"
            "Please report the following issue on Github: https://github.com/lux-org/lux/issues \n",
            stacklevel=2,
        )
        warnings.warn(traceback.format_exc())
        display(self.to_pandas())
