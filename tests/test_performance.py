from .context import lux
import pytest
import pandas as pd
import time
# To run the script and see the printed result, run:
# python -m pytest -s tests/test_performance.py
def test_q1_performance_census():
	url = 'https://github.com/lux-org/lux-datasets/blob/master/data/census.csv?raw=true'
	df = pd.read_csv(url)
	tic = time.perf_counter()
	df.set_intent(["education","age"])
	df._repr_html_()
	toc = time.perf_counter()
	delta = toc - tic
	df._repr_html_()
	toc2 = time.perf_counter()
	delta2 = toc2 - toc
	print(f"1st display Performance: {delta:0.4f} seconds")
	print(f"2nd display Performance: {delta2:0.4f} seconds")
	assert delta < 4.0, "The recommendations on Census dataset took a total of {delta:0.4f} seconds, longer than expected."
	assert delta2 < 0.1<delta, "Subsequent display of recommendations on Census dataset took a total of {delta2:0.4f} seconds, longer than expected."