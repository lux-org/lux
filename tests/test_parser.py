import pandas as pd
import lux

def test_case1():
	ldf = pd.read_csv("lux/data/car.csv")
	ldf.setContext(["Horsepower"])
	assert(type(ldf.context[0]) is lux.Spec)
	assert(ldf.context[0].type == "attribute")
	assert(ldf.context[0].attribute == "Horsepower")

def test_case2():
	ldf = pd.read_csv("lux/data/car.csv")
	ldf.setContext(["Horsepower", lux.Spec("MilesPerGal",channel="x")])
	assert(type(ldf.context[0]) is lux.Spec)
	assert(ldf.context[0].type == "attribute")
	assert(ldf.context[0].attribute == "Horsepower")
	assert(type(ldf.context[1]) is lux.Spec)
	assert(ldf.context[1].type == "attribute")
	assert(ldf.context[1].attribute == "MilesPerGal")

def test_case3():
	ldf = pd.read_csv("lux/data/car.csv")
	ldf.setContext(["Horsepower", "Origin=USA"])
	assert(type(ldf.context[0]) is lux.Spec)
	assert(ldf.context[0].type == "attribute")
	assert(ldf.context[0].attribute == "Horsepower")
	assert(type(ldf.context[1]) is lux.Spec)
	assert(ldf.context[1].attribute == "Origin")
	assert(ldf.context[1].type == "value")
	assert(ldf.context[1].value == "USA")

def test_case4():
	ldf = pd.read_csv("lux/data/car.csv")
	ldf.setContext(["Horsepower", "Origin=USA|Japan"])
	assert(type(ldf.context[0]) is lux.Spec)
	assert(ldf.context[0].type == "attribute")
	assert(ldf.context[0].attribute == "Horsepower")
	assert(type(ldf.context[1]) is lux.Spec)
	assert(ldf.context[1].attribute == "Origin")
	assert(ldf.context[1].type == "valueGroup")
	assert(ldf.context[1].value == ["USA","Japan"])

def test_case5():
	ldf = pd.read_csv("lux/data/car.csv")
	ldf.setContext([["Horsepower", "MilesPerGal", "Weight"], "Origin=USA"])
	assert(type(ldf.context[0]) is lux.Spec)
	assert(ldf.context[0].attribute == ["Horsepower", "MilesPerGal", "Weight"])
	assert(ldf.context[0].type == "attributeGroup")
	assert(type(ldf.context[1]) is lux.Spec)
	assert(ldf.context[1].attribute == "Origin")
	assert(ldf.context[1].type == "value")
	assert(ldf.context[1].value == "USA")

	ldf.setContext(["Horsepower/MilesPerGal/Weight", "Origin=USA"])
	assert(type(ldf.context[0]) is lux.Spec)
	assert(ldf.context[0].attribute == ["Horsepower", "MilesPerGal", "Weight"])
	assert(ldf.context[0].type == "attributeGroup")
	assert(type(ldf.context[1]) is lux.Spec)
	assert(ldf.context[1].attribute == "Origin")
	assert(ldf.context[1].type == "value")
	assert(ldf.context[1].value == "USA")