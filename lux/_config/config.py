'''
This config file was largely borrowed from Pandas config.py set_action functionality.
For more resources, see https://github.com/pandas-dev/pandas/blob/master/pandas/_config
'''
from collections import namedtuple
from typing import Any, Callable, Dict, Iterable, List, Optional

RegisteredOption = namedtuple("RegisteredOption", "key function validator")

# holds registered option metadata
_registered_actions: Dict[str, RegisteredOption] = {}

def _get_action(pat: str, silent: bool = False):
	return _registered_actions[pat]

class DictWrapper:
	def __init__(self, d: Dict[str, Any], prefix: str = ""):
		object.__setattr__(self, "d", d)
		object.__setattr__(self, "prefix", prefix)
	def __init__(self, d: Dict[str, RegisteredOption], prefix: str = ""):
		object.__setattr__(self, "d", d)
		object.__setattr__(self, "prefix", prefix)

	def __setattr__(self, key: str, val: Any) -> None:
		prefix = object.__getattribute__(self, "prefix")
		if prefix:
			prefix += "."
		prefix += key
		if key in self.d and not isinstance(self.d[key], dict):
			_set_option(prefix, val)
		else:
			raise OptionError("You can only set the value of existing options")

	def __getattr__(self, key: str):
		prefix = object.__getattribute__(self, "prefix")
		if prefix:
			prefix += "."
		prefix += key
		try:
			v = object.__getattribute__(self, "d")[key]
		except KeyError as err:
			raise OptionError("No such option") from err
		if isinstance(v, dict):
			return DictWrapper(v, prefix)
		else:
			return _get_action(prefix)

	def __getactions__(self):
		l = []
		for key in self.__dir__():
			l.append(self.__getattr__(key))
		return l

	def __len__(self):
		return len(list(self.d.keys()))

	def __dir__(self) -> Iterable[str]:
		return list(self.d.keys())

actions = DictWrapper(_registered_actions)


def register_action(
    key: str = "",
    function: Optional[Callable[[Any], Any]] = None,
    validator: Optional[Callable[[Any], Any]] = None,
) -> None:

	key = key.lower()
	if key in _registered_actions:
		raise ValueError(f"Option '{key}' has already been registered")
	if function:
		if not is_callable(function):
			raise ValueError(f"{k} is a python keyword")
	if not function:
		raise ValueError(f"{k} is a python keyword")

	if validator:
		if not is_callable(validator):
			raise ValueError(f"{k} is a python keyword")

	_registered_actions[key] = RegisteredOption(
        key=key, function=function, validator=validator
    )

def remove_action(
    key: str = "",
) -> None:

	key = key.lower()
	if key not in _registered_actions:
		raise ValueError(f"Option '{key}' has not been registered")

	del _registered_actions[key]

def is_callable(obj) -> bool:
	"""
    Parameters
    ----------
    `obj` - the object to be checked
    Returns
    -------
    validator - returns True if object is callable
        raises ValueError otherwise.
    """
	if not callable(obj):
		raise ValueError("Value must be a callable")
	return True

