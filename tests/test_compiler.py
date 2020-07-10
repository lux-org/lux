from .context import lux
import pytest
import pandas as pd

def test_underspecified_no_vis(test_show_more):
	no_view_actions = ["Correlation", "Distribution", "Category","Temporal"]
	df = pd.read_csv("lux/data/car.csv")
	test_show_more(df, no_view_actions)
	assert len(df.current_view) == 0

	# test only one filter context case.
	df.set_context([lux.Spec(attribute ="Origin", filter_op="=", value="USA")])
	test_show_more(df, no_view_actions)
	assert len(df.current_view) == 0

def test_underspecified_single_vis(test_show_more):
	one_view_actions = ["Enhance", "Filter", "Generalize"]
	df = pd.read_csv("lux/data/car.csv")
	df.set_context([lux.Spec(attribute ="MilesPerGal"), lux.Spec(attribute ="Weight")])
	assert len(df.current_view) == 1
	assert df.current_view[0].mark == "scatter"
	for attr in df.current_view[0].spec_lst: assert attr.data_model == "measure"
	for attr in df.current_view[0].spec_lst: assert attr.data_type == "quantitative"
	test_show_more(df, one_view_actions)

def test_underspecified_vis_collection(test_show_more):
	multiple_view_actions = ["Current Views"]

	df = pd.read_csv("lux/data/car.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y') # change pandas dtype for the column "Year" to datetype

	df.set_context([lux.Spec(attribute = ["Horsepower", "Weight", "Acceleration"]), lux.Spec(attribute ="Year", channel="x")])
	assert len(df.current_view) == 3
	assert df.current_view[0].mark == "line"
	for vc in df.current_view:
		assert (vc.get_attr_by_channel("x")[0].attribute == "Year")
	test_show_more(df, multiple_view_actions)

	df.set_context([lux.Spec(attribute ="?"), lux.Spec(attribute ="Year", channel="x")])
	assert len(df.current_view) == len(list(df.columns)) - 1 # we remove year by year so its 8 vis instead of 9
	for vc in df.current_view:
		assert (vc.get_attr_by_channel("x")[0].attribute == "Year")
	test_show_more(df, multiple_view_actions)

	df.set_context([lux.Spec(attribute ="?", data_type="quantitative"), lux.Spec(attribute ="Year")])
	assert len(df.current_view) == len([view.get_attr_by_data_type("quantitative") for view in df.current_view]) # should be 5
	test_show_more(df, multiple_view_actions)

	df.set_context([lux.Spec(attribute ="?", data_model="measure"), lux.Spec(attribute="MilesPerGal", channel="y")])
	for vc in df.current_view:
		print (vc.get_attr_by_channel("y")[0].attribute == "MilesPerGal")
	test_show_more(df, multiple_view_actions)

	df.set_context([lux.Spec(attribute ="?", data_model="measure"), lux.Spec(attribute ="?", data_model="measure")])
	assert len(df.current_view) == len([view.get_attr_by_data_model("measure") for view in df.current_view]) #should be 25
	test_show_more(df, multiple_view_actions)

@pytest.fixture
def test_show_more():
	def test_show_more_function(df, actions):
		df.show_more()
		assert (len(df._rec_info) > 0)
		for rec in df._rec_info:
			assert (rec["action"] in actions)
	return test_show_more_function

def test_parse():
	df = pd.read_csv("lux/data/car.csv")
	df.set_context([lux.Spec("Origin=?"), lux.Spec(attribute ="MilesPerGal")])
	assert len(df.current_view) == 3

	df = pd.read_csv("lux/data/car.csv")
	df.set_context([lux.Spec("Origin=?"), lux.Spec("MilesPerGal")])
	assert len(df.current_view) == 3
def test_underspecified_vis_collection_zval():
	# check if the number of charts is correct
	df = pd.read_csv("lux/data/car.csv")
	df.set_context([lux.Spec(attribute ="Origin", filter_op="=", value="?"), lux.Spec(attribute ="MilesPerGal")])
	assert len(df.current_view) == 3

	#does not work
	# df = pd.read_csv("lux/data/cars.csv")
	# df.set_context([lux.Spec(attribute = ["Origin","Cylinders"], filter_op="=",value="?"),lux.Spec(attribute = ["Horsepower"]),lux.Spec(attribute = "Weight")])
	# assert len(df.current_view) == 8

def test_sort_bar():
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

def test_specified_vis_collection():
	df = pd.read_csv("lux/data/cars.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y')  # change pandas dtype for the column "Year" to datetype

	df.set_context(
		[lux.Spec(attribute="Horsepower"),lux.Spec(attribute="Brand"), lux.Spec(attribute = "Origin",value=["Japan","USA"])])
	assert len(df.current_view) == 2

	df.set_context(
		[lux.Spec(attribute=["Horsepower","Weight"]),lux.Spec(attribute="Brand"), lux.Spec(attribute = "Origin",value=["Japan","USA"])])
	assert len(df.current_view) == 4

# 	# test if z axis has been filtered correctly
	chart_titles = [view.title for view in df.current_view.collection]
	assert "Origin = USA" and "Origin = Japan" in chart_titles
	assert "Origin = Europe" not in chart_titles


def test_specified_channel_enforced_vis_collection():
	df = pd.read_csv("lux/data/cars.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y')  # change pandas dtype for the column "Year" to datetype
	df.set_context(
		[lux.Spec(attribute="?"),lux.Spec(attribute="MilesPerGal",channel="x")])
	for view in df.current_view:
		check_attribute_on_channel(view, "MilesPerGal", "x")

def test_autoencoding_scatter():
	# No channel specified
	df = pd.read_csv("lux/data/cars.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y')  # change pandas dtype for the column "Year" to datetype
	df.set_context([lux.Spec(attribute="MilesPerGal"), lux.Spec(attribute="Weight")])
	view = df.current_view[0]
	check_attribute_on_channel(view, "MilesPerGal", "x")
	check_attribute_on_channel(view, "Weight", "y")

	# Partial channel specified
	df.set_context([lux.Spec(attribute="MilesPerGal", channel="y"), lux.Spec(attribute="Weight")])
	view = df.current_view[0]
	check_attribute_on_channel(view, "MilesPerGal", "y")
	check_attribute_on_channel(view, "Weight", "x")

	# Full channel specified
	df.set_context([lux.Spec(attribute="MilesPerGal", channel="y"), lux.Spec(attribute="Weight", channel="x")])
	view = df.current_view[0]
	check_attribute_on_channel(view, "MilesPerGal", "y")
	check_attribute_on_channel(view, "Weight", "x")
	# Duplicate channel specified
	with pytest.raises(ValueError):
		# Should throw error because there should not be columns with the same channel specified
		df.set_context([lux.Spec(attribute="MilesPerGal", channel="x"), lux.Spec(attribute="Weight", channel="x")])

	
def test_autoencoding_histogram():
	# No channel specified
	df = pd.read_csv("lux/data/cars.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y')  # change pandas dtype for the column "Year" to datetype
	df.set_context([lux.Spec(attribute="MilesPerGal", channel="y")])
	view = df.current_view[0]
	check_attribute_on_channel(view, "MilesPerGal", "y")

	# Record instead of count
	# df.set_context([lux.Spec(attribute="MilesPerGal",channel="x")])
	# assert df.current_view[0].get_attr_by_channel("x")[0].attribute == "MilesPerGal"
	# assert df.current_view[0].get_attr_by_channel("y")[0].attribute == "count()"

def test_autoencoding_line_chart():
	df = pd.read_csv("lux/data/cars.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y')  # change pandas dtype for the column "Year" to datetype
	df.set_context([lux.Spec(attribute="Year"), lux.Spec(attribute="Acceleration")])
	view = df.current_view[0]
	check_attribute_on_channel(view, "Year", "x")
	check_attribute_on_channel(view, "Acceleration", "y")

	# Partial channel specified
	df.set_context([lux.Spec(attribute="Year", channel="y"), lux.Spec(attribute="Acceleration")])
	view = df.current_view[0]
	check_attribute_on_channel(view, "Year", "y")
	check_attribute_on_channel(view, "Acceleration", "x")

	# Full channel specified
	df.set_context([lux.Spec(attribute="Year", channel="y"), lux.Spec(attribute="Acceleration", channel="x")])
	view = df.current_view[0]
	check_attribute_on_channel(view, "Year", "y")
	check_attribute_on_channel(view, "Acceleration", "x")

	with pytest.raises(ValueError):
		# Should throw error because there should not be columns with the same channel specified
		df.set_context([lux.Spec(attribute="Year", channel="x"), lux.Spec(attribute="Acceleration", channel="x")])

def test_autoencoding_color_line_chart():
	df = pd.read_csv("lux/data/cars.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y')  # change pandas dtype for the column "Year" to datetype
	df.set_context([lux.Spec(attribute="Year"), lux.Spec(attribute="Acceleration"), lux.Spec(attribute="Origin")])

	view = df.current_view[0]

	check_attribute_on_channel(view, "Year", "x")
	check_attribute_on_channel(view, "Acceleration", "y")
	check_attribute_on_channel(view, "Origin", "color")

def test_autoencoding_color_scatter_chart():
	df = pd.read_csv("lux/data/cars.csv")
	df["Year"] = pd.to_datetime(df["Year"], format='%Y')  # change pandas dtype for the column "Year" to datetype
	df.set_context([lux.Spec(attribute="Horsepower"), lux.Spec(attribute="Acceleration"), lux.Spec(attribute="Origin")])
	view = df.current_view[0]
	check_attribute_on_channel(view, "Origin", "color")

	df.set_context([lux.Spec(attribute="Horsepower"), lux.Spec(attribute="Acceleration", channel="color"), lux.Spec(attribute="Origin")])
	view = df.current_view[0]
	check_attribute_on_channel(view, "Acceleration", "color")

def test_populate_options():
	from lux.compiler.Compiler import Compiler
	df = pd.read_csv("lux/data/cars.csv")
	df.set_context([lux.Spec(attribute="?"), lux.Spec(attribute="MilesPerGal")])
	col_set = set()
	for specOptions in Compiler.populate_wildcard_options(df.context, df)["attributes"]:
		for spec in specOptions:
			col_set.add(spec.attribute)
	assert list_equal(list(col_set), list(df.columns))

	df.set_context([lux.Spec(attribute="?", data_model="measure"), lux.Spec(attribute="MilesPerGal")])
	col_set = set()
	for specOptions in Compiler.populate_wildcard_options(df.context, df)["attributes"]:
		for spec in specOptions:
			col_set.add(spec.attribute)
	assert list_equal(list(col_set), ['Acceleration', 'Weight', 'Horsepower', 'MilesPerGal', 'Displacement'])

def list_equal(l1, l2):
    l1.sort()
    l2.sort()
    return l1==l2

def check_attribute_on_channel(view, attr_name, channelName):
	assert view.get_attr_by_channel(channelName)[0].attribute == attr_name
