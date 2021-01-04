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
