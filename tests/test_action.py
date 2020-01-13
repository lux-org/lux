from .context import lux
import pytest
import numpy as np 
import math
def test_correlation():
	dataset = lux.Dataset("lux/data/cars.csv",schema=[{"Year":{"dataType":"date"}}])
	dobj = lux.DataObj(dataset,[lux.Column(["Horsepower","Weight","Acceleration","Displacement"]),lux.Column("MilesPerGal")])
	dobj.correlation()
	# Make sure that all correlation result in a single score
	assert np.sum(list(map(lambda x: hasattr(x,"score"),dobj.compiled.collection)))==True*len(dobj.compiled.collection)
	
def test_distribution():
	dataset = lux.Dataset("lux/data/cars.csv",schema=[{"Year":{"dataType":"date"}}])
	dobj = lux.DataObj(dataset,[lux.Column(["Horsepower","Weight","Acceleration","Displacement"])])
	dobj.distribution()
	assert dobj.compiled.collection[0].score != 0

def test_generalize():
	dataset = lux.Dataset("lux/data/cars.csv",schema=[{"Year":{"dataType":"date"}}])

	dobj = lux.DataObj(dataset,[lux.Column("Acceleration"), lux.Column("Horsepower")])
	result = dobj.generalize()
	# assert math.isclose(generalizedList[0].score, 40952, rel_tol=0.01) 
	# assert math.isclose(generalizedList[1].score, 6092.2, rel_tol=0.01) 
	assert len(result.resultsJSON[0]["collection"].collection) == 2

	dobj = lux.DataObj(dataset,[lux.Column("MilesPerGal"),lux.Column("Weight"),lux.Column("Origin")])
	result = dobj.generalize()
	assert len(result.resultsJSON[0]["collection"].collection) == 3 

	dobj = lux.DataObj(dataset,[lux.Column("Acceleration"), lux.Column("Horsepower"),lux.Row(fAttribute="Origin",fVal="USA")])
	result = dobj.generalize()
	assert len(result.resultsJSON[0]["collection"].collection) == 3
	# dobj = lux.DataObj(dataset,[lux.Column(["Acceleration", "Horsepower"]),lux.Row(fAttribute="Origin",fVal="USA")])
	# dobj.generalize()
	# assert math.isclose(generalizedList[0].score, 29167, rel_tol=0.01) 
	# assert math.isclose(generalizedList[1].score,3672.6, rel_tol=0.01) 
	# assert len(dobj.recommendation["collection"].collection) == 3

	# dobj = lux.DataObj(dataset,[lux.Column(["Acceleration", "Horsepower"]),lux.Column("MilesPerGal")])
	# dobj.generalize()
	# assert math.isclose(generalizedList[0].score, 40952, rel_tol=0.01) 
	# assert len(dobj.recommendation["collection"].collection) == 3

	#dobj = lux.DataObj(dataset,[lux.Column("?",dataModel="measure"), lux.Column("MilesPerGal")])
	#generalizedList = dobj.generalize()
	#assert generalizedList[0].score == 392
	#assert len(generalizedList) == 6