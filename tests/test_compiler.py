from .context import lux
import pytest
import pandas as pd

def test_underspecifiedNoVis(test_showMore):
	noViewActions = ["Correlation", "Distribution", "Category"]
	df = pd.read_csv("lux/data/car.csv")
	test_showMore(df,noViewActions)
	assert len(df.currentView)==0

	# test only one filter context case.
	df.setContext([lux.Spec(attribute = "Origin", filter_op="=",value="USA")])
	test_showMore(df,noViewActions)
	assert len(df.currentView)==0

def test_underspecifiedSingleVis(test_showMore):
	oneViewActions = ["Enhance", "Filter", "Generalize"]
	df = pd.read_csv("lux/data/car.csv")
	df.setContext([lux.Spec(attribute = "MilesPerGal"),lux.Spec(attribute = "Weight")])
	assert len(df.currentView)==1
	assert df.currentView[0].mark == "scatter"
	for attr in df.currentView[0].spec_lst: assert attr.data_model=="measure"
	for attr in df.currentView[0].spec_lst: assert attr.data_type=="quantitative"
	test_showMore(df,oneViewActions)

def test_underspecifiedVisCollection(test_showMore):
	multipleViewActions = ["Current Views"]

	df = pd.read_csv("lux/data/car.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y') # change pandas dtype for the column "Year" to datetype

	df.setContext([lux.Spec(attribute = ["Horsepower","Weight","Acceleration"]),lux.Spec(attribute = "Year",channel="x")])
	assert len(df.currentView)==3
	assert df.currentView[0].mark == "line"
	for vc in df.currentView:
		assert (vc.get_attr_by_channel("x")[0].attribute == "Year")
	test_showMore(df,multipleViewActions)

	df.setContext([lux.Spec(attribute = "?"),lux.Spec(attribute = "Year",channel="x")])
	assert len(df.currentView) == len(list(df.columns))-1 # we remove year by year so its 8 vis instead of 9
	for vc in df.currentView:
		assert (vc.get_attr_by_channel("x")[0].attribute == "Year")
	test_showMore(df,multipleViewActions)

	df.setContext([lux.Spec(attribute = "?",data_type="quantitative"),lux.Spec(attribute = "Year")])
	assert len(df.currentView) == len([view.get_attr_by_data_type("quantitative") for view in df.view_collection]) # should be 5
	test_showMore(df,multipleViewActions)

	df.setContext([lux.Spec(attribute = "?", data_model="measure"),lux.Spec(attribute="MilesPerGal",channel="y")])
	for vc in df.currentView:
		print (vc.get_attr_by_channel("y")[0].attribute == "MilesPerGal")
	test_showMore(df,multipleViewActions)

	df.setContext([lux.Spec(attribute = "?", data_model="measure"),lux.Spec(attribute = "?", data_model="measure")])
	assert len(df.currentView) == len([view.get_attr_by_data_model("measure") for view in df.currentView]) #should be 25
	test_showMore(df,multipleViewActions)

@pytest.fixture
def test_showMore():
	def test_showMore_function(df, actions):
		df.show_more()
		assert (len(df._rec_info) > 0)
		for rec in df._rec_info:
			assert (rec["action"] in actions)
	return test_showMore_function

def test_parse():
	df = pd.read_csv("lux/data/car.csv")
	df.setContext([lux.Spec("Origin=?"),lux.Spec(attribute = "MilesPerGal")])
	assert len(df.currentView)==3

	df = pd.read_csv("lux/data/car.csv")
	df.setContext([lux.Spec("Origin=?"),lux.Spec("MilesPerGal")])
	assert len(df.currentView)==3
def test_underspecifiedVisCollection_Zval():
	# check if the number of charts is correct
	df = pd.read_csv("lux/data/car.csv")
	df.setContext([lux.Spec(attribute = "Origin", filter_op="=",value="?"),lux.Spec(attribute = "MilesPerGal")])
	assert len(df.currentView)==3

	#does not work
	# df = pd.read_csv("lux/data/cars.csv")
	# df.setContext([lux.Spec(attribute = ["Origin","Cylinders"], filter_op="=",value="?"),lux.Spec(attribute = ["Horsepower"]),lux.Spec(attribute = "Weight")])
	# assert len(df.currentView) == 8

def test_sortBar():
	from lux.compiler.Compiler import Compiler
	from lux.view.View import View
	df = pd.read_csv("lux/data/car.csv")
	view = View([lux.Spec(attribute="Acceleration",data_model="measure",data_type="quantitative"),
				lux.Spec(attribute="Origin",data_model="dimension",data_type="nominal")])
	Compiler.determine_encoding(df, view)
	assert view.mark == "bar"
	assert view.spec_lst[1].sort == ''

	df = pd.read_csv("lux/data/car.csv")
	view = View([lux.Spec(attribute="Acceleration",data_model="measure",data_type="quantitative"),
				lux.Spec(attribute="Name",data_model="dimension",data_type="nominal")])
	Compiler.determine_encoding(df, view)
	assert view.mark == "bar"
	assert view.spec_lst[1].sort == 'ascending'

def test_specifiedVisCollection():
	df = pd.read_csv("lux/data/cars.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y')  # change pandas dtype for the column "Year" to datetype

	df.setContext(
		[lux.Spec(attribute="Horsepower"),lux.Spec(attribute="Brand"), lux.Spec(attribute = "Origin",value=["Japan","USA"])])
	assert len(df.view_collection) == 2

	df.setContext(
		[lux.Spec(attribute=["Horsepower","Weight"]),lux.Spec(attribute="Brand"), lux.Spec(attribute = "Origin",value=["Japan","USA"])])
	assert len(df.currentView) == 4

# 	# test if z axis has been filtered correctly
	chartTitles = [view.title for view in df.currentView.collection]
	assert "Origin = USA" and "Origin = Japan" in chartTitles
	assert "Origin = Europe" not in chartTitles


def test_specifiedChannelEnforcedVisCollection():
	df = pd.read_csv("lux/data/cars.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y')  # change pandas dtype for the column "Year" to datetype
	df.setContext(
		[lux.Spec(attribute="?"),lux.Spec(attribute="MilesPerGal",channel="x")])
	for view in df.currentView:
		checkAttributeOnChannel(view, "MilesPerGal", "x")

def test_autoencodingScatter():
	# No channel specified
	df = pd.read_csv("lux/data/cars.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y')  # change pandas dtype for the column "Year" to datetype
	df.setContext([lux.Spec(attribute="MilesPerGal"),lux.Spec(attribute="Weight")])
	view = df.currentView[0]
	checkAttributeOnChannel(view, "MilesPerGal", "x")
	checkAttributeOnChannel(view, "Weight", "y")

	# Partial channel specified
	df.setContext([lux.Spec(attribute="MilesPerGal", channel="y"),lux.Spec(attribute="Weight")])
	view = df.currentView[0]
	checkAttributeOnChannel(view, "MilesPerGal", "y")
	checkAttributeOnChannel(view, "Weight", "x")

	# Full channel specified
	df.setContext([lux.Spec(attribute="MilesPerGal", channel="y"),lux.Spec(attribute="Weight",channel="x")])
	view = df.currentView[0]
	checkAttributeOnChannel(view, "MilesPerGal", "y")
	checkAttributeOnChannel(view, "Weight", "x")
	# Duplicate channel specified
	with pytest.raises(ValueError):
		# Should throw error because there should not be columns with the same channel specified
		df.setContext([lux.Spec(attribute="MilesPerGal", channel="x"), lux.Spec(attribute="Weight", channel="x")])

	
def test_autoencodingHistogram():
	# No channel specified
	df = pd.read_csv("lux/data/cars.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y')  # change pandas dtype for the column "Year" to datetype
	df.setContext([lux.Spec(attribute="MilesPerGal",channel="y")])
	view = df.currentView[0]
	checkAttributeOnChannel(view, "MilesPerGal", "y")

	# Record instead of count
	# df.setContext([lux.Spec(attribute="MilesPerGal",channel="x")])
	# assert df.currentView[0].get_attr_by_channel("x")[0].attribute == "MilesPerGal"
	# assert df.currentView[0].get_attr_by_channel("y")[0].attribute == "count()"

def test_autoencodingLineChart():
	df = pd.read_csv("lux/data/cars.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y')  # change pandas dtype for the column "Year" to datetype
	df.setContext([lux.Spec(attribute="Year"),lux.Spec(attribute="Acceleration")])
	view = df.currentView[0]
	checkAttributeOnChannel(view, "Year", "x")
	checkAttributeOnChannel(view, "Acceleration", "y")

	# Partial channel specified
	df.setContext([lux.Spec(attribute="Year", channel="y"),lux.Spec(attribute="Acceleration")])
	view = df.currentView[0]
	checkAttributeOnChannel(view, "Year", "y")
	checkAttributeOnChannel(view, "Acceleration", "x")

	# Full channel specified
	df.setContext([lux.Spec(attribute="Year", channel="y"),lux.Spec(attribute="Acceleration", channel="x")])
	view = df.currentView[0]
	checkAttributeOnChannel(view, "Year", "y")
	checkAttributeOnChannel(view, "Acceleration", "x")

	with pytest.raises(ValueError):
		# Should throw error because there should not be columns with the same channel specified
		df.setContext([lux.Spec(attribute="Year", channel="x"), lux.Spec(attribute="Acceleration", channel="x")])

def test_autoencodingColorLineChart():
	df = pd.read_csv("lux/data/cars.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y')  # change pandas dtype for the column "Year" to datetype
	df.setContext([lux.Spec(attribute="Year"),lux.Spec(attribute="Acceleration"),lux.Spec(attribute="Origin")])

	view = df.currentView[0]

	checkAttributeOnChannel(view,"Year","x")
	checkAttributeOnChannel(view,"Acceleration","y")
	checkAttributeOnChannel(view,"Origin","color")

def test_autoencodingColorScatterChart():
	df = pd.read_csv("lux/data/cars.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y')  # change pandas dtype for the column "Year" to datetype
	df.setContext([lux.Spec(attribute="Horsepower"),lux.Spec(attribute="Acceleration"),lux.Spec(attribute="Origin")])
	view = df.currentView[0]
	checkAttributeOnChannel(view,"Origin","color")

	df.setContext([lux.Spec(attribute="Horsepower"),lux.Spec(attribute="Acceleration",channel="color"),lux.Spec(attribute="Origin")])
	view = df.currentView[0]
	checkAttributeOnChannel(view,"Acceleration","color")

def test_populateOptions():
	from lux.compiler.Compiler import Compiler
	df = pd.read_csv("lux/data/cars.csv")
	df.setContext([lux.Spec(attribute="?"), lux.Spec(attribute="MilesPerGal")])
	colSet = set()
	for specOptions in Compiler.populate_wildcard_options(df.context, df)["attributes"]:
		for spec in specOptions:
			colSet.add(spec.attribute)
	assert listEqual(list(colSet), list(df.columns))

	df.setContext([lux.Spec(attribute="?",data_model="measure"), lux.Spec(attribute="MilesPerGal")])
	colSet = set()
	for specOptions in Compiler.populate_wildcard_options(df.context, df)["attributes"]:
		for spec in specOptions:
			colSet.add(spec.attribute)
	assert listEqual(list(colSet), ['Acceleration', 'Weight', 'Horsepower', 'MilesPerGal', 'Displacement'])

def listEqual(l1,l2):
    l1.sort()
    l2.sort()
    return l1==l2

def checkAttributeOnChannel(view,attr_name,channelName):
	assert view.get_attr_by_channel(channelName)[0].attribute == attr_name
