from __future__ import annotations
from typing import List, Union, Callable, Dict
from lux.history.event import Event
class History():
	"""
	History maintains a list of past Pandas operations performed on the dataframe
	Currently only supports custom overridden functions (head, tail, info, describe)
	"""
	def __init__(self):
		self._events=[]
	
	def __getitem__(self, key):
		return self._events[key]
	def __setitem__(self, key, value):
		self._events[key] = value
	def __len__(self):
		return len(self._events)
	def __repr__(self):
		event_repr=[]
		for event in self._events:
			event_repr.append(event.__repr__())
		return "["+'\n'.join(event_repr)+"]"
	def append_event(self,name,*args,**kwargs):
		event = Event(name,*args,**kwargs)
		self._events.append(event)