from .context import lux
import pytest
import pandas as pd
import time
def test_q1_performance_census():
	df = pd.read_csv("lux/data/census.csv")
	tic = time.perf_counter()
	df.set_intent(["education","age"])
	df._repr_html_()
	toc = time.perf_counter()
	delta = toc - tic
	print(f"Overall Performance: {delta:0.4f} seconds")
	assert delta < 10, "The recommendations on Census dataset took a total of {delta:0.4f} seconds, longer than expected."