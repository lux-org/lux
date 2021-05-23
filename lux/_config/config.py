"""
This config file was largely borrowed from Pandas config.py set_action functionality.
For more resources, see https://github.com/pandas-dev/pandas/blob/master/pandas/_config
"""
from collections import namedtuple
from typing import Any, Callable, Dict, Iterable, List, Optional, Union
import lux
import warnings

RegisteredOption = namedtuple("RegisteredOption", "name action display_condition args")


class Config:
    """
    Class for Lux configurations applied globally across entire session
    """

    def __init__(self):
        self._default_display = "pandas"
        self.plotting_style = None
        self.SQLconnection = ""
        self.executor = None
        # holds registered option metadata
        self.actions: Dict[str, RegisteredOption] = {}
        # flags whether or not an action has been registered or removed and should be re-rendered by frame.py
        self.update_actions: Dict[str, bool] = {}
        self.update_actions["flag"] = False
        self._plotting_backend = "vegalite"
        self._plotting_scale = 1
        self._topk = 15
        self._sort = "descending"
        self._pandas_fallback = True
        self._interestingness_fallback = True
        self.heatmap_bin_size = 40
        #####################################
        #### Optimization Configurations ####
        #####################################
        self._sampling_start = 100000
        self._sampling_cap = 1000000
        self._sampling_flag = True
        self._heatmap_flag = True
        self.lazy_maintain = True
        self.early_pruning = True
        self.early_pruning_sample_cap = 30000
        # Apply sampling only if the dataset is 150% larger than the sample cap
        self.early_pruning_sample_start = self.early_pruning_sample_cap * 1.5
        self.streaming = False
        self.render_widget = True

    @property
    def topk(self):
        return self._topk

    @topk.setter
    def topk(self, k: Union[int, bool]):
        """
        Setting parameter to display top k visualizations in each action

        Parameters
        ----------
        k : Union[int,bool]
            False: if display all visualizations (no top-k)
            k: number of visualizations to display
        """
        if isinstance(k, int) or isinstance(k, bool):
            self._topk = k
        else:
            warnings.warn(
                "Parameter to lux.config.topk must be an integer or a boolean.",
                stacklevel=2,
            )

    @property
    def sort(self):
        return self._sort

    @sort.setter
    def sort(self, flag: Union[str]):
        """
        Setting parameter to determine sort order of each action

        Parameters
        ----------
        flag : Union[str]
            "none", "ascending","descending"
            No sorting, sort by ascending order, sort by descending order
        """
        flag = flag.lower()
        if isinstance(flag, str) and flag in ["none", "ascending", "descending"]:
            self._sort = flag
        else:
            warnings.warn(
                "Parameter to lux.config.sort must be one of the following: 'none', 'ascending', or 'descending'.",
                stacklevel=2,
            )

    @property
    def pandas_fallback(self):
        return self._pandas_fallback

    @pandas_fallback.setter
    def pandas_fallback(self, fallback: bool) -> None:
        """
        Parameters
        ----------
        fallback : bool
            If an error occurs, whether or not to raise an exception or fallback to default Pandas.
        """
        if type(fallback) == bool:
            self._pandas_fallback = fallback
        else:
            warnings.warn(
                "The flag for Pandas fallback must be a boolean.",
                stacklevel=2,
            )

    @property
    def interestingness_fallback(self):
        return self._interestingness_fallback

    @interestingness_fallback.setter
    def interestingness_fallback(self, fallback: bool) -> None:
        """
        Parameters
        ----------
        fallback : bool
            If an error occurs while calculating interestingness, whether or not
            to raise an exception or fallback to default Pandas.
        """
        if type(fallback) == bool:
            self._interestingness_fallback = fallback
        else:
            warnings.warn(
                "The flag for interestingness fallback must be a boolean.",
                stacklevel=2,
            )

    @property
    def sampling_cap(self):
        """
        Parameters
        ----------
        sample_number : int
            Cap on the number of rows to sample. Must be larger than _sampling_start
        """
        return self._sampling_cap

    @sampling_cap.setter
    def sampling_cap(self, sample_number: int) -> None:
        """
        Parameters
        ----------
        sample_number : int
            Cap on the number of rows to sample. Must be larger than _sampling_start
        """
        if type(sample_number) == int:
            assert sample_number >= self._sampling_start
            self._sampling_cap = sample_number
        else:
            warnings.warn(
                "The cap on the number samples must be an integer.",
                stacklevel=2,
            )

    @property
    def sampling_start(self):
        """
        Parameters
        ----------
        sample_number : int
            Number of rows required to begin sampling. Must be smaller or equal to _sampling_cap

        """
        return self._sampling_start

    @sampling_start.setter
    def sampling_start(self, sample_number: int) -> None:
        """
        Parameters
        ----------
        sample_number : int
            Number of rows required to begin sampling. Must be smaller or equal to _sampling_cap

        """
        if type(sample_number) == int:
            assert sample_number <= self._sampling_cap
            self._sampling_start = sample_number
        else:
            warnings.warn(
                "The sampling starting point must be an integer.",
                stacklevel=2,
            )

    @property
    def sampling(self):
        """
        Parameters
        ----------
        sample_flag : bool
            Whether or not sampling will occur.
        """
        return self._sampling_flag

    @sampling.setter
    def sampling(self, sample_flag: bool) -> None:
        """
        Parameters
        ----------
        sample_flag : bool
            Whether or not sampling will occur.
        """
        if type(sample_flag) == bool:
            self._sampling_flag = sample_flag
        else:
            warnings.warn(
                "The flag for sampling must be a boolean.",
                stacklevel=2,
            )

    @property
    def heatmap(self):
        """
        Parameters
        ----------
        heatmap_flag : bool
            Whether or not a heatmap will be used instead of a scatter plot.
        """
        return self._heatmap_flag

    @heatmap.setter
    def heatmap(self, heatmap_flag: bool) -> None:
        """
        Parameters
        ----------
        heatmap_flag : bool
            Whether or not a heatmap will be used instead of a scatter plot.
        """
        if type(heatmap_flag) == bool:
            self._heatmap_flag = heatmap_flag
        else:
            warnings.warn(
                "The flag for enabling/disabling heatmaps must be a boolean.",
                stacklevel=2,
            )

    @property
    def default_display(self):
        """
        Set the widget display to show Pandas by default or Lux by default
        Parameters
        ----------
        type : str
            Default display type, can take either the string `lux` or `pandas` (regardless of capitalization)
        """
        return self._default_display

    @default_display.setter
    def default_display(self, type: str) -> None:
        """
        Set the widget display to show Pandas by default or Lux by default
        Parameters
        ----------
        type : str
            Default display type, can take either the string `lux` or `pandas` (regardless of capitalization)
        """
        if type.lower() == "lux":
            self._default_display = "lux"
        elif type.lower() == "pandas":
            self._default_display = "pandas"
        else:
            warnings.warn(
                "Unsupported display type. Default display option should either be `lux` or `pandas`.",
                stacklevel=2,
            )

    @property
    def plotting_backend(self):
        return self._plotting_backend

    @plotting_backend.setter
    def plotting_backend(self, type: str) -> None:
        """
        Set the widget display to show Vegalite by default or Matplotlib by default
        Parameters
        ----------
        type : str
                Default display type, can take either the string `vegalite` or `matplotlib` (regardless of capitalization)
        """
        if type.lower() == "vegalite" or type.lower() == "altair":
            self._plotting_backend = "vegalite"
        elif type.lower() == "matplotlib":
            self._plotting_backend = "matplotlib_svg"
        else:
            warnings.warn(
                "Unsupported plotting backend. Lux currently only support 'altair', 'vegalite', or 'matplotlib'",
                stacklevel=2,
            )

    @property
    def plotting_scale(self):
        return self._plotting_scale

    @plotting_scale.setter
    def plotting_scale(self, scale: float) -> None:
        """
        Set the scale factor for charts displayed in Lux.
        ----------
        type : float (default = 1.0)
        """
        scale = float(scale) if isinstance(scale, int) else scale
        if isinstance(scale, float) and scale > 0:
            self._plotting_scale = scale
        else:
            warnings.warn(
                "Scaling factor for charts must be a positive float.",
                stacklevel=2,
            )

    def _get_action(self, pat: str, silent: bool = False):
        return lux.actions[pat]

    def register_action(
        self,
        name: str = "",
        action: Callable[[Any], Any] = None,
        display_condition: Optional[Callable[[Any], Any]] = None,
        *args,
    ) -> None:
        """
        Registers the provided action globally in lux

        Parameters
        ----------
        name : str
                the name of the action
        action : Callable[[Any], Any]
                the function used to generate the recommendations
        display_condition : Callable[[Any], Any]
                the function to check whether or not the function should be applied
        args: Any
                any additional arguments the function may require
        """
        if action:
            if not callable(action):
                raise ValueError("Action must be a callable")
        if display_condition:
            if not callable(display_condition):
                raise ValueError("Display condition must be a callable")
        self.actions[name] = RegisteredOption(
            name=name, action=action, display_condition=display_condition, args=args
        )
        self.update_actions["flag"] = True

    def remove_action(self, name: str = "") -> None:
        """
        Removes the provided action globally in lux

        Parameters
        ----------
        name : str
                the name of the action to remove
        """
        if name not in self.actions:
            raise ValueError(f"Option '{name}' has not been registered")

        del self.actions[name]
        self.update_actions["flag"] = True

    def set_SQL_connection(self, connection):
        """
        Sets SQL connection to a database

        Parameters:
            connection : SQLAlchemy connectable, str, or sqlite3 connection
                For more information, `see here <https://docs.sqlalchemy.org/en/13/core/connections.html>`__
        """
        self.set_executor_type("SQL")
        self.SQLconnection = connection

    def set_executor_type(self, exe):
        if exe == "SQL":
            from lux.executor.SQLExecutor import SQLExecutor

            self.executor = SQLExecutor()
        elif exe == "Pandas":
            from lux.executor.PandasExecutor import PandasExecutor

            self.SQLconnection = ""
            self.executor = PandasExecutor()
        else:
            raise ValueError("Executor type must be either 'Pandas' or 'SQL'")


def warning_format(message, category, filename, lineno, file=None, line=None):
    return "%s:%s: %s:%s\n" % (filename, lineno, category.__name__, message)
