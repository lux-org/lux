def rename_from_history(_input_df):
    try:
        mre = _input_df.history._events[-1]
        c = mre.cols[0] if len(mre.cols) else mre.op_name
        _input_df = _input_df.rename(columns = {_input_df.columns[0]: c})
        
        return _input_df
    except IndexError:
        return _input_df