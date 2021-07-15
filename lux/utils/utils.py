#  Copyright 2019-2020 The Lux Authors.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import lux


def convert_to_list(x):
    """
    "a" --> ["a"]
    ["a","b"] --> ["a","b"]
    """
    if type(x) != list:
        return [x]
    else:
        return x

def convert_slice_to_list(x, columns):
    # stop should ideally be the length of columns
    columns = columns.tolist()
    ifnone = lambda a, b: b if a is None else a
    step = ifnone(x.step, 1)
    # for slice like 'a':'e', or "Name":"Cylinders"
    if isinstance(x.start, str) or isinstance(x.stop, str):
        start_index = columns.index(ifnone(x.start, columns[0])) 
        # since the loc is successful, we are sure that this index won't raise an error
        stop_index = columns.index(ifnone(x.stop, columns[-1]))
        return [columns[i] for i in range(start_index, stop_index + 1)]
        # +1 since in range, this point is excluded
    # for normal slice like 1:5
    else:
        return list(range(ifnone(x.start, 0), ifnone(x.stop, len(columns))+ step, step))

def convert_indices_to_columns(column_names, tup):
    '''
        convert column indices that might be used in iloc function to corresponding column names
        the supported `index` could be int, a list, a slice object  
    '''
    if len(tup) == 1:
        # here it is of the tupe type, but the length is only 1, for example (1,)
        tup = (tup[0], slice(None, None, None))
    
    index = tup[1]
    ret_columns = []
    if isinstance(index, int):
        ret_columns = [column_names[index]]
    elif isinstance(index, list) or isinstance(index, np.ndarray):
        # it could be possible that `index` is a list of boolean values or integers. 
        if all(isinstance(x, bool) for x in index):
            ret_columns = [column_names[col_index] for col_index, included in enumerate(index) if included]
        elif all(isinstance(x, int) for x in index):
            ret_columns = [column_names[col_index] for col_index in index]
    elif isinstance(index, slice):
        column_indices = convert_slice_to_list(index, column_names) # do not know why the end is not included
        for col_index in column_indices:
            if col_index < len(column_names): 
                # it is allowed that some indices in the slice object not in the columns of the dataframe
                ret_columns.append(column_names[col_index])
    else:
        ret_columns = None
    
    ret_columns = list(set(ret_columns)) # remove duplicates
    if ret_columns and (len(ret_columns) == len(column_names)):
        # then it does not provide any more information
        ret_columns = []
    return ret_columns

def convert_names_to_columns(column_names, tup):
    '''
        convert column indices that might be used in loc function to corresponding column names
        the supported `index` could be int, a list, a slice object  
    '''
    if len(tup) == 1:
        # here it is of the tupe type, but the length is only 1, for example (1,)
        tup = (tup[0], slice(None, None, None))
    
    index = tup[1]
    ret_columns = []
    if isinstance(index, str):
        ret_columns = [index]
    elif isinstance(index, list) or isinstance(index, np.ndarray):
        # it could be possible that `index` is a list of boolean values. 
        if all(isinstance(x, bool) for x in index):
            ret_columns = [column_names[col_index] for col_index, included in enumerate(index) if included]
        else:
            ret_columns =  index
    elif isinstance(index, slice):
        # for slice object, loc allows that some columns to be extracted does not exist
        # while loc will examine whether all columns exist in the list case.
        columns = convert_slice_to_list(index, column_names)
        for col_name in columns:
            if col_name in column_names:
                ret_columns.append(col_name)
    else:
        ret_columns = None

    ret_columns = list(set(ret_columns)) # remove duplicates
    if ret_columns and (len(ret_columns) == len(column_names)):
        # In this case it does not provide any more information
        ret_columns = []
    return ret_columns

def pandas_to_lux(df):
    from lux.core.frame import LuxDataFrame

    values = df.values.tolist()
    ldf = LuxDataFrame(values, columns=df.columns)
    return ldf


def get_attrs_specs(intent):
    if intent is None:
        return []
    spec_obj = list(filter(lambda x: x.value == "", intent))
    return spec_obj


def get_filter_specs(intent):
    if intent is None:
        return []
    spec_obj = list(filter(lambda x: x.value != "", intent))
    return spec_obj


def check_import_lux_widget():
    import pkgutil

    if pkgutil.find_loader("luxwidget") is None:
        raise Exception(
            "luxwidget is not installed. Run `pip install luxwidget' to install the Jupyter widget.\nSee more at: https://github.com/lux-org/lux-widget"
        )


def get_agg_title(clause):
    attr = str(clause.attribute)
    if clause.aggregation is None:
        if len(attr) > 25:
            return attr[:15] + "..." + attr[-10:]
        return f"{attr}"
    elif attr == "Record":
        return f"Number of Records"
    else:
        if len(attr) > 15:
            return f"{clause._aggregation_name.capitalize()} of {attr[:15]}..."
        return f"{clause._aggregation_name.capitalize()} of {attr}"


def check_if_id_like(df, attribute):
    import re

    # Strong signals
    # so that aggregated reset_index fields don't get misclassified
    high_cardinality = df.cardinality[attribute] > 500
    attribute_contain_id = re.search(r"id|ID|iD|Id", str(attribute)) is not None
    almost_all_vals_unique = df.cardinality[attribute] >= 0.98 * len(df)
    is_string = pd.api.types.is_string_dtype(df[attribute])
    if is_string:
        # For string IDs, usually serial numbers or codes with alphanumerics have a consistent length (eg., CG-39405) with little deviation. For a high cardinality string field but not ID field (like Name or Brand), there is less uniformity across the string lengths.
        if len(df) > 50:
            if lux.config.executor.name == "PandasExecutor":
                sampled = df[attribute].sample(50, random_state=99)
            else:
                from lux.executor.SQLExecutor import SQLExecutor

                sampled = SQLExecutor.execute_preview(df, preview_size=50)
        else:
            sampled = df[attribute]
        str_length_uniformity = sampled.apply(lambda x: type(x) == str and len(x)).std() < 3
        return (
            high_cardinality
            and (attribute_contain_id or almost_all_vals_unique)
            and str_length_uniformity
        )
    else:
        if len(df) >= 2:
            series = df[attribute]
            diff = series.diff()
            evenly_spaced = all(diff.iloc[1:] == diff.iloc[1])
        else:
            evenly_spaced = True
        if attribute_contain_id:
            almost_all_vals_unique = df.cardinality[attribute] >= 0.75 * len(df)
        return high_cardinality and (almost_all_vals_unique or evenly_spaced)


def like_nan(val):
    if isinstance(val, str):
        return val.lower() == "nan"
    elif isinstance(val, float) or isinstance(val, int):
        import math

        return math.isnan(val)


def like_geo(val):
    return isinstance(val, str) and val.lower() in {"state", "country"}


def matplotlib_setup(w, h):
    plt.ioff()
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_axisbelow(True)
    ax.grid(color="#dddddd")
    ax.spines["right"].set_color("#dddddd")
    ax.spines["top"].set_color("#dddddd")
    return fig, ax


def is_numeric_nan_column(series):
    if series.dtype == object:
        if series.hasnans:
            series = series.dropna()
        try:
            return True, series.astype("float")
        except Exception as e:
            return False, series
    else:
        return False, series
