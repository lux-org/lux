import lux
import pandas as pd
import math
import numpy as np
from lux.vis.VisList import VisList
from lux._config.config import actions

def custom_action(ldf):
	if (actions.__len__() > 0):
		for action_name in actions.__dir__():
			validator = actions.__getattr__(action_name).validator(ldf)
			if validator:
				function = actions.__getattr__(action_name).function(ldf)
				recommendation = {"action":function["action"], "description":function["description"]}
				recommendation["collection"] = function["collection"]
				return recommendation
			else:
				return None
	else:
		return None