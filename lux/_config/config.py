"""
This config file was largely borrowed from Pandas config.py set_action functionality.
For more resources, see https://github.com/pandas-dev/pandas/blob/master/pandas/_config
"""
from collections import namedtuple
from typing import Any, Callable, Dict, Iterable, List, Optional
import warnings

RegisteredOption = namedtuple("RegisteredOption", "name action display_condition args")

# holds registered option metadata
_registered_actions: Dict[str, RegisteredOption] = {}
# flags whether or not an action has been registered or removed and should be re-rendered by frame.py
update_actions: Dict[str, bool] = {}
update_actions["flag"] = False


class OptionError(AttributeError, KeyError):
    """
    Exception for pandas.options, backwards compatible with KeyError
    checks
    """


def _get_action(pat: str, silent: bool = False):
    return _registered_actions[pat]


class DictWrapper:
    def __init__(self, d: Dict[str, Any], prefix: str = ""):
        object.__setattr__(self, "d", d)
        object.__setattr__(self, "prefix", prefix)

    def __init__(self, d: Dict[str, RegisteredOption], prefix: str = ""):
        object.__setattr__(self, "d", d)
        object.__setattr__(self, "prefix", prefix)

    def __getattr__(self, name: str):
        """
        Gets a specific registered action by id

        Parameters
        ----------
        name : str
                the name of the action
        Return
        -------
        DictWrapper object for the action
        """
        prefix = object.__getattribute__(self, "prefix")
        if prefix:
            prefix += "."
        prefix += name
        try:
            v = object.__getattribute__(self, "d")[name]
        except KeyError as err:
            raise OptionError("No such option") from err
        if isinstance(v, dict):
            return DictWrapper(v, prefix)
        else:
            return _get_action(prefix)

    def __getactions__(self):
        """
        Gathers all currently registered actions in a list of DictWrapper

        Return
        -------
        List of DictWrapper objects that are registered
        """
        l = []
        for name in self.__dir__():
            l.append(self.__getattr__(name))
        return l

    def __len__(self):
        return len(list(self.d.keys()))

    def __dir__(self) -> Iterable[str]:
        return list(self.d.keys())


actions = DictWrapper(_registered_actions)


def register_action(
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
        is_callable(action)

    if display_condition:
        is_callable(display_condition)
    _registered_actions[name] = RegisteredOption(
        name=name, action=action, display_condition=display_condition, args=args
    )
    update_actions["flag"] = True


def remove_action(name: str = "") -> None:
    """
    Removes the provided action globally in lux

    Parameters
    ----------
    name : str
            the name of the action to remove
    """
    if name not in _registered_actions:
        raise ValueError(f"Option '{name}' has not been registered")

    del _registered_actions[name]
    update_actions["flag"] = True


def is_callable(obj) -> bool:
    """
    Parameters
    ----------
    obj: Any
            the object to be checked

    Returns
    -------
    validator : bool
            returns True if object is callable
            raises ValueError otherwise.
    """
    if not callable(obj):
        raise ValueError("Value must be a callable")
    return True


class Config:
    def __init__(self):
        self._default_display = "pandas"
        self.renderer = "altair"
        self.plot_config = None
        self.SQLconnection = ""
        self.executor = None

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


config = Config()


def warning_format(message, category, filename, lineno, file=None, line=None):
    return "%s:%s: %s:%s\n" % (filename, lineno, category.__name__, message)
