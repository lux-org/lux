import lux
import pandas as pd
import math
import numpy as np
from lux.vis.VisList import VisList
from lux._config.config import actions

def custom_action(ldf):
	print("hi")
	if (actions.__len__() > 0):
		for action_name in actions.__dir__():
			print("here1")
			validator = actions.__getattr__(action_name).validator(ldf)
			if validator:
				function = actions.__getattr__(action_name).function(ldf)
				print("here2")

				recommendation = {"action":function["action"], "description":function["description"]}
				print("here3")

				recommendation["collection"] = function["collection"]
				return recommendation
	else:
		print("none found")