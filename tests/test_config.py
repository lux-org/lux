#  Copyright 2019-2020 The Lux Authors.
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from .context import lux
import pytest
import pandas as pd
import time
from lux.vis.VisList import VisList
import lux

# To run the script and see the printed result, run:
def test_q0_default_actions_registered():
	df = pd.read_csv("lux/data/car.csv")
	df._repr_html_()
	assert("Distribution" in df.recommendation)
	assert(len(df.recommendation["Distribution"]) > 0)

	assert("Occurrence" in df.recommendation)
	assert(len(df.recommendation["Occurrence"]) > 0)

	assert("Temporal" in df.recommendation)
	assert(len(df.recommendation["Temporal"]) > 0)

	assert("Correlation" in df.recommendation)
	assert(len(df.recommendation["Correlation"]) > 0)

def test_q1_fail_validator():
	df = pd.read_csv("lux/data/car.csv")
	def random_categorical(ldf):
		intent = [lux.Clause("?",data_type="nominal")]
		vlist = VisList(intent,ldf)
		for vis in vlist:
			vis.score = 10
		vlist = vlist.topK(15)
		return {"action":"bars", "description": "Random list of Bar charts", "collection": vlist}
	def contain_horsepower(df):
		for clause in df.intent:
			if clause.get_attr() == "Horsepower":
				return True
		return False
	lux.register_action("bars", random_categorical, contain_horsepower)
	df._repr_html_()
	assert("bars" not in df.recommendation)

def test_q2_pass_validator():
	def random_categorical(ldf):
		intent = [lux.Clause("?",data_type="nominal")]
		vlist = VisList(intent,ldf)
		for vis in vlist:
			vis.score = 10
		vlist = vlist.topK(15)
		return {"action":"bars", "description": "Random list of Bar charts", "collection": vlist}
	def contain_horsepower(df):
		for clause in df.intent:
			if clause.get_attr() == "Horsepower":
				return True
		return False
	df = pd.read_csv("lux/data/car.csv")
	lux.register_action("bars", random_categorical, contain_horsepower)
	df.set_intent(["Acceleration", "Horsepower"])
	df._repr_html_()
	assert(len(df.recommendation["bars"]) > 0)
	assert("bars" in df.recommendation)

def test_q3_no_validator():
	df = pd.read_csv("lux/data/car.csv")
	def random_categorical(ldf):
		intent = [lux.Clause("?",data_type="nominal")]
		vlist = VisList(intent,ldf)
		for vis in vlist:
			vis.score = 10
		vlist = vlist.topK(15)
		return {"action":"bars", "description": "Random list of Bar charts", "collection": vlist}
	lux.register_action("bars", random_categorical)
	df._repr_html_()
	assert(len(df.recommendation["bars"]) > 0)
	assert("bars" in df.recommendation)

def test_q4_no_function():
	df = pd.read_csv("lux/data/car.csv")
	with pytest.raises(ValueError,match="No parameter function found"):
		lux.register_action("bars")

def test_q5_invalid_function():
	df = pd.read_csv("lux/data/car.csv")
	with pytest.raises(ValueError,match="Value must be a callable"):
		lux.register_action("bars", "not a Callable")

def test_q6_invalid_validator():
	df = pd.read_csv("lux/data/car.csv")
	def random_categorical(ldf):
		intent = [lux.Clause("?",data_type="nominal")]
		vlist = VisList(intent,ldf)
		for vis in vlist:
			vis.score = 10
		vlist = vlist.topK(15)
		return {"action":"bars", "description": "Random list of Bar charts", "collection": vlist}
	with pytest.raises(ValueError,match="Value must be a callable"):
		lux.register_action("bars", random_categorical, "not a Callable")

def test_q7_remove_action():
	def random_categorical(ldf):
		intent = [lux.Clause("?",data_type="nominal")]
		vlist = VisList(intent,ldf)
		for vis in vlist:
			vis.score = 10
		vlist = vlist.topK(15)
		return {"action":"bars", "description": "Random list of Bar charts", "collection": vlist}
	def contain_horsepower(df):
		for clause in df.intent:
			if clause.get_attr() == "Horsepower":
				return True
		return False
	df = pd.read_csv("lux/data/car.csv")
	lux.register_action("bars", random_categorical, contain_horsepower)
	df.set_intent(["Acceleration", "Horsepower"])
	df._repr_html_()
	assert("bars" in df.recommendation)
	assert(len(df.recommendation["bars"]) > 0)
	lux.remove_action("bars")
	df._repr_html_()
	assert("bars" not in df.recommendation)

def test_q8_remove_invalid_action():
	df = pd.read_csv("lux/data/car.csv")
	with pytest.raises(ValueError,match="Option 'bars' has not been registered"):
		lux.remove_action("bars")

def test_q9_remove_default_actions():
	df = pd.read_csv("lux/data/car.csv")
	df._repr_html_()

	lux.remove_action("Distribution")
	df._repr_html_()
	assert("Distribution" not in df.recommendation)

	lux.remove_action("Occurrence")
	df._repr_html_()
	assert("Occurrence" not in df.recommendation)

	lux.remove_action("Temporal")
	df._repr_html_()
	assert("Temporal" not in df.recommendation)

	lux.remove_action("Correlation")
	df._repr_html_()
	assert("Correlation" not in df.recommendation)

	assert(len(df.recommendation) == 0)

	def random_categorical(ldf):
		intent = [lux.Clause("?",data_type="nominal")]
		vlist = VisList(intent,ldf)
		for vis in vlist:
			vis.score = 10
		vlist = vlist.topK(15)
		return {"action":"bars", "description": "Random list of Bar charts", "collection": vlist}
	def contain_horsepower(df):
		for clause in df.intent:
			if clause.get_attr() == "Horsepower":
				return True
		return False
	df = pd.read_csv("lux/data/car.csv")
	lux.register_action("bars", random_categorical, contain_horsepower)
	df.set_intent(["Acceleration", "Horsepower"])
	df._repr_html_()
	assert("bars" in df.recommendation)
	assert(len(df.recommendation["bars"]) > 0)
