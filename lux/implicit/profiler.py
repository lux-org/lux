import pandas as pd
import tokenize
import io
import altair as alt

def get_implicit_intent(userCode, df_name_dict):
    """
    MAIN METHOD:
    Takes in string of user code and analyzes.

    Parameters
    ----------
    userCode: STRING 
        All of the user's python code in one string.

    Returns
    ----------
    same as get_recent_history() below
    """
    
    #print("Beginning PA...")
    
    df_names = list(df_name_dict.keys())

    all_cols = set()
    for l in df_name_dict.values(): all_cols.update(l)

    
    # build distribution over variables accessed in that df (with regex)
    try:
        f_calls, col_refs = get_recent_history(userCode, df_names, all_cols)
    
    except Exception as e:
        print("PA FAILED!\n", e)
        f_calls = [("", [], "")]
        col_refs = []


    #print(f"PA complete. \n\tf_calls: {f_calls}\n\tcol_refs: {col_refs}")

    # match that to a vis case
    # vis = get_vis_off_recent_func(f_calls, all_df_dict) # TODO use this in Lux rec

    return f_calls, col_refs

   

def get_recent_history(userCodeString, df_names, all_cols):
    """
    Takes in a string and tokenizes the input as valid python code to perform program analysis

    Parameters
    ----------
    userCodeString: STRING 
        The user's python code
    
    df_names: LIST 
        Names of all lux df objects in the user's session
    
    all_cols: SET 
        Column names from all dataframes in session

    Returns
    ----------
    f_calls: LIST 
        Function calls most recent last. [(df_name, [columns], 'value_counts'), ...]
	
    col_refs: DICT 
        {col_name: num_refs}
    """

    # static items
    ignore_tokens = [60, 61, 4,0]
    funcs = ["value_counts", "crosstab", "describe", "unique", "query", "groupby", "agg"] # filter

    f_calls = []
    col_refs = {}

    # tokenize
    buf = io.StringIO(userCodeString)
    tokens = tokenize.generate_tokens(buf.readline)

    curr_line = 1
    curr_df = None
    rec_cols = []
    for token in tokens:
        if token.type not in ignore_tokens:
            this_line = token.start[0]
            # get rid of quotes so can match to col names and df names
            this_str = token.string.replace('"', "")
            this_str = this_str.replace("'", "")

            if this_line != curr_line:
                curr_df = None
                rec_cols = []
                curr_line = this_line

            if token.type in [1, 3]: # string or name
                if not curr_df and this_str in df_names:
                    curr_df = this_str
                elif this_str in funcs:
                    t = (curr_df, rec_cols, this_str)
                    f_calls.append(t)
                elif this_str in all_cols:
                    rec_cols.append(this_str)
                    if this_str in col_refs: 
                        col_refs[this_str] += 1
                    else:
                        col_refs[this_str] = 1

            #print(f"Type {token.type}.{token.exact_type}:\t\t{token.start} - {token.end} \t{token.string}\t\t\t{token.line}")
    
    return f_calls, col_refs


def get_vis_off_recent_func(f_calls, all_df_dict):
    '''
    In: array of function calls from oldest to newest, each of form (df_name, [col_names], f_name)

    TODO
    - use other columns to suggest other visualizations
    - use distribution of column access as additional encodings
    - rec multiple vis instead of just 1

    - Do this in Lux rec rather than here (using intent)...

    '''

    # match function case
    last_call = f_calls[-1]
    df_name, col_names, f_name = last_call
    df = all_df_dict[df_name]

#     print("Last call: ", last_call)
  
    if not len(col_names) and f_name != "describe":
        raise ValueError(f"No column names associated with the function call {f_name}")

    if f_name == "value_counts" or f_name == "unique":
        # greedy select first column
        vis = alt.Chart(df)\
            .mark_bar()\
            .encode(x=col_names[0], y="count()")
    
    elif f_name == "crosstab":
        df = df.reset_index()
        col_names = list(df.columns)
        
        vis = alt.Chart(df).transform_fold(
                col_names[1:],
            ).mark_rect().encode(
            alt.X("key:N"),
            alt.Y(f"{col_names[0]}:O"),
            alt.Color('value:Q', scale=alt.Scale(scheme="blues")))
    
    elif f_name == "describe":
        numeric_cols = list(df.dtypes[(df.dtypes == "float64") | (df.dtypes == "int64")].index)
        _facets = []
        for c in numeric_cols:
            _facets.append(alt.Chart(df).mark_boxplot().encode(y=f"{c}:Q"))
        vis = alt.hconcat(*_facets)

    elif f_name == "query":
        # TODO do this, not supporting most selection types rn 
        vis = None

    elif f_name == "groupby" or f_name == "agg":
        # TODO do this better -- find out which function is being called on each column 
        df = df.reset_index()
        if type(df.columns) == pd.core.indexes.multi.MultiIndex:
#             print("Is multi")
            nc = [' '.join(col).strip() for col in df.columns.values]
            df.columns = nc
            col_names =  nc

        vis = alt.Chart(df).transform_fold(
            col_names[1:],
        ).mark_point().encode( # TODO change this mark type depending on what the dtype is 
            x=col_names[0],
            y='value:Q',
            color='key:N'
        )
    
    else:
        raise ValueError(f"[ERROR] Unable to match vis for {f_name}")
        vis = None

    return vis 