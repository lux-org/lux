import lux
from lux.interestingness.interestingness import interestingness
from lux.compiler.Compiler import Compiler
from lux.utils import utils

from lux.vis.Vis import Vis
from lux.vis.VisList import VisList

#for benchmarking
import time
def indexgroup(ldf):
	#for benchmarking
	if ldf.toggle_benchmarking == True:
		tic = time.perf_counter()
	recommendation = {"action":"Index-Group",
					"description":"Shows charts of possible visualizations with respect to the index."}
	collection = []
	index_column_name = ldf.index.name
	for attribute in ldf.columns:
		vis = Vis([index_column_name,lux.Clause(attribute,aggregation=None)],ldf[attribute].reset_index())
		collection.append(vis)
	vlst = VisList(collection)
	# Note that we are not computing interestingness score here because we want to preserve the arrangement of the aggregated data
	
	recommendation["collection"] = vlst
	#for benchmarking
	if ldf.toggle_benchmarking == True:
		toc = time.perf_counter()
		print(f"Performed enhance action in {toc - tic:0.4f} seconds")
	return recommendation