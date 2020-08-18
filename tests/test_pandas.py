from .context import lux
import pytest
import pandas as pd

# def test_df_to_series():
#     # Ensure metadata is kept when going from df to series
#     df = pd.read_csv("lux/data/car.csv")
#     df._repr_html_() # compute metadata
#     assert df.cardinality is not None
#     series = df["Weight"]
#     assert isinstance(series,lux.core.series.LuxSeries), "Derived series is type LuxSeries."
#     assert df["Weight"]._metadata == ['name','_intent', 'data_type_lookup', 'data_type', 'data_model_lookup', 'data_model', 'unique_values', 'cardinality', 'min_max', 'plot_config', '_current_vis', '_widget', '_recommendation'], "Metadata is lost when going from Dataframe to Series."
#     assert df.cardinality is not None, "Metadata is lost when going from Dataframe to Series."
#     assert series.name == "Weight", "Pandas Series original `name` property not retained."