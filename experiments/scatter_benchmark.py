import papermill as pm
import pandas as pd
import numpy as np
import json

# experiment_name = "sampled_scatter"
# ["sampled_scatter","basic_scatter","heatmap","manual_heatmap","manual_heatmap_2x_coarse"]
for experiment_name in ["sampled_scatter_20000"]:
# for experiment_name in ["manual_binned_scatter"]:
	# trial_range = np.geomspace(10, 1e5, num=9)
	# trial_range = np.geomspace(10, 1e5, num=9)
	trial_range = np.geomspace(10, 1e5, num=17)
	trial = [] #[cell count, duration]
	for nPts in trial_range:
		# output_filename = f"uncolored_single_scatter_output_{nPts}.ipynb"
		output_filename = "output.ipynb"
		# papermill basic_scatter.ipynb output.ipynb -p numPoints 1000000 --execute-timeout 1000 
		pm.execute_notebook(
			f'{experiment_name}.ipynb',
			output_filename,
			parameters = dict(numPoints=nPts)
		)
		count = 0 
		with open(output_filename) as json_file:
			data = json.load(json_file)
			for cell in data['cells']:
				# For testing out Lux Performance
				# if "outputs" in cell and len(cell["outputs"]) > 0:
				# 	if cell["outputs"][0]["output_type"] == "display_data":
				# 		count += 1
				# For testing Pandas Performance
				if cell["execution_count"]==5:
					duration1 = cell["metadata"]["papermill"]["duration"]
				# For testing Altair Output Performance
				if cell["execution_count"]==6:
					duration2 = cell["metadata"]["papermill"]["duration"]
			trial.append([nPts,duration1,duration2])
			print (nPts,duration1,duration2)

	trial_df = pd.DataFrame(trial,columns=["nPts","pandas cost","altair cost"])
	trial_df.to_csv(f"{experiment_name}.csv",index=None)
