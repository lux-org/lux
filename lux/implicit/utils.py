import os
import importlib.util
import pandas as pd


'''
from https://stackoverflow.com/questions/4383571/importing-files-from-different-folder?page=2&tab=votes#tab-top

Will likely need to change for diff environments...

# This works if at same level of directory (f_name cant have .py at end)
# import importlib
# mod = importlib.import_module(f_name)

'''
def import_module_by_path(path):
    name = os.path.splitext(os.path.basename(path))[0]
                            
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

'''
In ipynb this can be done with 
%who_ls to get variable names then check types to see which are df

'''
def get_dfs_from_mod(mod):
    dfs = {}
    
    for item in dir(mod):
        if not item.startswith("__"):
            a = getattr(mod, item)
            
            if type(a) == pd.DataFrame: # TODO may want this to also include series or other dtypes
                dfs[item] = a
    
    return dfs