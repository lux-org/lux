import pandas as pd
import lux

def test_case1():
	ldf = pd.read_csv("lux/data/car.csv")
	ldf.set_intent(["Horsepower"])
	assert(type(ldf.intent[0]) is lux.Clause)
	assert(ldf.intent[0].attribute == "Horsepower")

def test_case2():
	ldf = pd.read_csv("lux/data/car.csv")
	ldf.set_intent(["Horsepower", lux.Clause("MilesPerGal", channel="x")])
	assert(type(ldf.intent[0]) is lux.Clause)
	assert(ldf.intent[0].attribute == "Horsepower")
	assert(type(ldf.intent[1]) is lux.Clause)
	assert(ldf.intent[1].attribute == "MilesPerGal")

def test_case3():
	ldf = pd.read_csv("lux/data/car.csv")
	ldf.set_intent(["Horsepower", "Origin=USA"])
	assert(type(ldf.intent[0]) is lux.Clause)
	assert(ldf.intent[0].attribute == "Horsepower")
	assert(type(ldf.intent[1]) is lux.Clause)
	assert(ldf.intent[1].attribute == "Origin")
	assert(ldf.intent[1].value == "USA")

def test_case4():
	ldf = pd.read_csv("lux/data/car.csv")
	ldf.set_intent(["Horsepower", "Origin=USA|Japan"])
	assert(type(ldf.intent[0]) is lux.Clause)
	assert(ldf.intent[0].attribute == "Horsepower")
	assert(type(ldf.intent[1]) is lux.Clause)
	assert(ldf.intent[1].attribute == "Origin")
	assert(ldf.intent[1].value == ["USA","Japan"])

def test_case5():
	ldf = pd.read_csv("lux/data/car.csv")
	ldf.set_intent([["Horsepower", "MilesPerGal", "Weight"], "Origin=USA"])
	assert(type(ldf.intent[0]) is lux.Clause)
	assert(ldf.intent[0].attribute == ["Horsepower", "MilesPerGal", "Weight"])
	assert(type(ldf.intent[1]) is lux.Clause)
	assert(ldf.intent[1].attribute == "Origin")
	assert(ldf.intent[1].value == "USA")

	ldf.set_intent(["Horsepower|MilesPerGal|Weight", "Origin=USA"])
	assert(type(ldf.intent[0]) is lux.Clause)
	assert(ldf.intent[0].attribute == ["Horsepower", "MilesPerGal", "Weight"])
	assert(type(ldf.intent[1]) is lux.Clause)
	assert(ldf.intent[1].attribute == "Origin")
	assert(ldf.intent[1].value == "USA")

def test_case6():
	ldf = pd.read_csv("lux/data/car.csv")
	ldf.set_intent(["Horsepower", "Origin=?"])
	assert(type(ldf.intent[0]) is lux.Clause)
	assert(ldf.intent[0].attribute == "Horsepower")
	assert(type(ldf.intent[1]) is lux.Clause)
	assert(ldf.intent[1].attribute == "Origin")
	assert(ldf.intent[1].value == ["USA","Japan","Europe"])

# TODO: Need to support this case
'''
lux.set_intent(["Horsepower","MPG","Acceleration"],"Origin")
	lux.set_intent("Horsepower/MPG/Acceleration", "Origin")
		--> [Clause(attr= ["Horsepower","MPG","Acceleration"], type= "attributeGroup")]
'''