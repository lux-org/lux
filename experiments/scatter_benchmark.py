import papermill as pm
import pandas as pd
import numpy as np
import json
# trial_range = np.geomspace(10, 1e3, num=3)
trial_range = np.geomspace(10, 1e8, num=8)
trial = [] #[cell count, duration]
for nPts in trial_range:
	# output_filename = f"uncolored_single_scatter_output_{nPts}.ipynb"
	output_filename = "output.ipynb"
	pm.execute_notebook(
		'uncolored_single_scatter.ipynb',
		output_filename,
		parameters = dict(numPoints=nPts)
	)
	count = 0 
	with open(output_filename) as json_file:
		data = json.load(json_file)
		for cell in data['cells']:
			if "outputs" in cell and len(cell["outputs"]) > 0:
				if cell["outputs"][0]["output_type"] == "display_data":
					count += 1
					duration = cell["metadata"]["papermill"]["duration"]
					trial.append([nPts,duration])
					print (nPts,duration)

trial_df = pd.DataFrame(trial,columns=["nPts","duration"])
trial_df.to_csv("experiment_result_metadata_precomputed.csv",index=None)
# print (trial_df)
# import matplotlib.pyplot as plt
# plt.xlabel('cell execution count')
# plt.ylabel('time (s)')
# plt.plot(trial_df["cell_count"], trial_df["duration"])
# plt.show()

