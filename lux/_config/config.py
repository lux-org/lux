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
    name = name.lower()
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
    name = name.lower()
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
        self._default_renderer = "altair"
        self._default_plot_config = None
        

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
    @property
    def default_renderer(self):
        return self._default_renderer
    
    @default_renderer.setter
    def default_renderer(self, type: str) -> None:
        """
        Set the widget display to use a particular renderer
        Parameters
        ----------
        type: str
                Choice of visualization rendering library, by default "altair"
        """
        self._default_renderer = type.lower()

    @property
    def default_plot_config(self):
        return self._default_plot_config
    
    @default_plot_config.setter
    def default_plot_config(self, config_func: Callable):
        """
        Modify plot aesthetic settings to all visualizations in the dataframe display
        Currently only supported for Altair visualizations
        Parameters
        ----------
        config_func : Callable
                A function that takes in an AltairChart (https://altair-viz.github.io/user_guide/generated/toplevel/altair.Chart.html) as input and returns an AltairChart as output

        Example
        ----------
        Changing the color of marks and adding a title for all charts displayed for this dataframe
        >>> df = pd.read_csv("lux/data/car.csv")
        >>> def changeColorAddTitle(chart):
                        chart = chart.configure_mark(color="red") # change mark color to red
                        chart.title = "Custom Title" # add title to chart
                        return chart
        >>> lux.config.default_plot_config = changeColorAddTitle
        >>> df
        """
        self._default_plot_config = config_func

    def clear_plot_config(self):
        self._default_plot_config = None



config = Config()
