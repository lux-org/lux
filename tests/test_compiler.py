from .context import lux
import pytest
def test_underspecifiedSingleVis():
	dataset = lux.Dataset("lux/data/cars.csv",schema=[{"Year":{"dataType":"date"}}])
	dobj = lux.DataObj(dataset,[lux.Column("MilesPerGal"),lux.Column("Weight")])
	assert dobj.spec[0].dataType == ""
	assert dobj.spec[0].dataModel == ""

	assert dobj.compiled.spec[0].dataType=="quantitative"
	assert dobj.compiled.spec[0].dataModel=="measure"
def test_underspecifiedVisCollection():
	
	dataset = lux.Dataset("lux/data/cars.csv",schema=[{"Year":{"dataType":"date"}}])
	dobj = lux.DataObj(dataset,[lux.Column(["Horsepower","Weight","Acceleration"]),lux.Column(["Year"],channel="x")])
	assert len(dobj.compiled.collection) ==3
	for obj in dobj.compiled.collection: 
		assert obj.getObjFromChannel("x")[0].columnName == "Year"

	dobj = lux.DataObj(dataset,[lux.Column("?"),lux.Column("Year",channel="x")])
	assert len(dobj.compiled.collection) == len(dobj.dataset.df.columns)
	# TODO: Doris need to debug showMe enforceSpecifiedChannel 2 dim, 0 msr (count()) cases
	# for obj in dobj.compiled.collection: 
	# 	assert obj.getObjFromChannel("x")[0].columnName == "Year"

	dobj = lux.DataObj(dataset,[lux.Column("?",dataModel="measure"),lux.Column("MilesPerGal",channel="y")])
	for obj in dobj.compiled.collection: 
		assert obj.getObjFromChannel("y")[0].columnName == "MilesPerGal"
	
	dobj = lux.DataObj(dataset,[lux.Column("?",dataModel="measure"),lux.Column("?",dataModel="measure")])
	assert len(dobj.compiled.collection) == 25
	# TODO: Jay: this example is not working, need pairwise combination of measure values (mostly counts now?)	
def test_underspecifiedVisCollection_Z():
	# check if the number of charts is correct
	dataset = lux.Dataset("lux/data/cars.csv",schema=[{"Year":{"dataType":"date"}}])
	dobj = lux.DataObj(dataset, [lux.Column("MilesPerGal"), lux.Row("Origin", "?")])
	assert type(dobj.compiled).__name__ == "DataObjCollection"
	assert len(dobj.compiled.collection) == 3

	dobj = lux.DataObj(dataset,[lux.Column("Horsepower"),lux.Column("Brand"),lux.Row("Origin",["Japan","USA"])])
	assert type(dobj.compiled).__name__ == "DataObjCollection"
	assert len(dobj.compiled.collection) == 2

	dobj = lux.DataObj(dataset,[lux.Column(["Horsepower","Weight"]),lux.Column("Brand"),lux.Row("Origin",["Japan","USA"])])
	assert len(dobj.compiled.collection) == 4

	# test ? command
	dobj = lux.DataObj(dataset,[lux.Column(["Horsepower","Weight"]),lux.Column("Brand"),lux.Row("Origin","?")])
	assert len(dobj.compiled.collection) == 6

	# test if z axis has been filtered correctly
	dobj = lux.DataObj(dataset,[lux.Column(["Horsepower","Weight"]),lux.Column("Brand"),lux.Row("Origin",["Japan","USA"])])
	chartTitles = list(dobj.compiled.get("title"))
	assert "Origin=USA" and "Origin=Japan" in chartTitles
	assert "Origin=Europe" not in chartTitles

	# test number of data points makes sense
	dobj = lux.DataObj(dataset,[lux.Column(["Horsepower"]),lux.Column("Brand"),lux.Row("Origin","?")])
	def getNumDataPoints(dObj):
		numRows = getattr(dObj, "dataset").df.shape[0]
		# Might want to write catch error if key not in field
		return numRows
	totalNumRows= sum(list(dobj.compiled.map(getNumDataPoints)))
	assert totalNumRows == 392

def test_autoencodingScatter():
	# No channel specified
	dataset = lux.Dataset("lux/data/cars.csv",schema=[{"Year":{"dataType":"date"}}])
	dobj = lux.DataObj(dataset,[lux.Column("MilesPerGal"),lux.Column("Weight")])
	assert dobj.compiled.getByColumnName("MilesPerGal")[0].channel == "x"
	assert dobj.compiled.getByColumnName("Weight")[0].channel == "y"
	# Partial channel specified
	dobj = lux.DataObj(dataset,[lux.Column("MilesPerGal", channel="y"),lux.Column("Weight")])
	assert dobj.compiled.getByColumnName("MilesPerGal")[0].channel == "y"
	assert dobj.compiled.getByColumnName("Weight")[0].channel == "x"

	# Full channel specified
	dobj = lux.DataObj(dataset,[lux.Column("MilesPerGal", channel="y"),lux.Column("Weight", channel="x")])
	assert dobj.compiled.getByColumnName("MilesPerGal")[0].channel == "y"
	assert dobj.compiled.getByColumnName("Weight")[0].channel == "x"
	# Duplicate channel specified
	with pytest.raises(ValueError):
		# Should throw error because there should not be columns with the same channel specified
		dobj = lux.DataObj(dataset,[lux.Column("MilesPerGal", channel="x"),lux.Column("Weight", channel="x")])

	
def test_autoencodingHistogram():
	dataset = lux.Dataset("lux/data/cars.csv",schema=[{"Year":{"dataType":"date"}}])
	
	# Partial channel specified
	dobj = lux.DataObj(dataset,[lux.Column("MilesPerGal",channel="y")])
	assert dobj.compiled.getByColumnName("MilesPerGal")[0].channel == "y"

	dobj = lux.DataObj(dataset,[lux.Column("MilesPerGal", channel="x")])
	assert dobj.compiled.getByColumnName("MilesPerGal")[0].channel == "x"
	assert dobj.compiled.getByColumnName("count()")[0].channel == "y"

def test_autoencodingLineChart():
	dataset = lux.Dataset("lux/data/cars.csv",schema=[{"Year":{"dataType":"date"}}])
	dobj = lux.DataObj(dataset,[lux.Column("Year"),lux.Column("Acceleration")])
	checkAttributeOnChannel(dobj,"Year","x")
	checkAttributeOnChannel(dobj,"Acceleration","y")
	# Partial channel specified
	dobj = lux.DataObj(dataset,[lux.Column("Year", channel="y"),lux.Column("Acceleration")])
	checkAttributeOnChannel(dobj,"Year","y")
	checkAttributeOnChannel(dobj,"Acceleration","x")

	# Full channel specified
	dobj = lux.DataObj(dataset,[lux.Column("Year", channel="y"),lux.Column("Acceleration", channel="x")])
	checkAttributeOnChannel(dobj,"Year","y")
	checkAttributeOnChannel(dobj,"Acceleration","x")
	# Duplicate channel specified
	with pytest.raises(ValueError):
		# Should throw error because there should not be columns with the same channel specified
		dobj = lux.DataObj(dataset,[lux.Column("Year", channel="x"),lux.Column("Acceleration", channel="x")])

def test_autoencodingColorLineChart():
	dataset = lux.Dataset("lux/data/cars.csv",schema=[{"Year":{"dataType":"date"}}])
	dobj = lux.DataObj(dataset,[lux.Column("Year"),lux.Column("Acceleration"),lux.Column("Origin")])
	checkAttributeOnChannel(dobj,"Year","x")
	checkAttributeOnChannel(dobj,"Acceleration","y")
	checkAttributeOnChannel(dobj,"Origin","color")
def test_autoencodingColorScatterChart():
	dataset = lux.Dataset("lux/data/cars.csv",schema=[{"Year":{"dataType":"date"}}])
	dobj = lux.DataObj(dataset,[lux.Column("Horsepower"),lux.Column("Acceleration"),lux.Column("Origin")])
	checkAttributeOnChannel(dobj,"Origin","color")
	dobj = lux.DataObj(dataset,[lux.Column("Horsepower"),lux.Column("Acceleration",channel="color"),lux.Column("Origin")])
	checkAttributeOnChannel(dobj,"Acceleration","color")
def test_populateOptions():
	from lux.compiler.Compiler import populateOptions
	dataset = lux.Dataset("lux/data/cars.csv",schema=[{"Year":{"dataType":"date"}}])
	dobj = lux.DataObj(dataset,[lux.Column("?"),lux.Column("MilesPerGal")])
	assert listEqual(populateOptions(dobj, dobj.spec[0]), list(dobj.dataset.df.columns))
	dobj = lux.DataObj(dataset,[lux.Column("?",dataModel="measure"),lux.Column("MilesPerGal")])
	assert listEqual(populateOptions(dobj, dobj.spec[0]), ['Acceleration','Weight','Horsepower','MilesPerGal','Displacement'])

def listEqual(l1,l2):
    l1.sort()
    l2.sort()
    return l1==l2
def checkAttributeOnChannel(dobj,attrName,channelName):
	assert dobj.compiled.getByColumnName(attrName)[0].channel == channelName
