"""
This config file was largely borrowed from Pandas config.py set_action functionality.
For more resources, see https://github.com/pandas-dev/pandas/blob/master/pandas/_config
"""
from collections import namedtuple
from typing import Any, Callable, Dict, Iterable, List, Optional
import warnings
import lux

RegisteredOption = namedtuple("RegisteredOption", "name action display_condition args")


class Config:
    def __init__(self):
        self._default_display = "pandas"
        self.renderer = "altair"
        self.plot_config = None
        self.SQLconnection = ""
        self.executor = None
        # holds registered option metadata
        self.actions: Dict[str, RegisteredOption] = {}
        # flags whether or not an action has been registered or removed and should be re-rendered by frame.py
        self.update_actions: Dict[str, bool] = {}
        self.update_actions["flag"] = False
        self._sampling_start = 10000
        self._sampling_cap = 30000
        self._sampling_flag = True
        self._heatmap_flag = True

    @property
    def sampling_cap(self):
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
        self.SQLconnection = connection

    def set_executor_type(self, exe):
        if exe == "SQL":
            import pkgutil

            if pkgutil.find_loader("psycopg2") is None:
                raise ImportError(
                    "psycopg2 is not installed. Run `pip install psycopg2' to install psycopg2 to enable the Postgres connection."
                )
            else:
                import psycopg2
            from lux.executor.SQLExecutor import SQLExecutor

            self.executor = SQLExecutor()
        else:
            from lux.executor.PandasExecutor import PandasExecutor

            self.executor = PandasExecutor()

    def set_SQL_connection(self, connection):
        self.SQLconnection = connection


def warning_format(message, category, filename, lineno, file=None, line=None):
    return "%s:%s: %s:%s\n" % (filename, lineno, category.__name__, message)
