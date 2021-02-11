#
# Code inspo from https://github.com/lckr/jupyterlab-variableInspector/blob/master/src/inspectorscripts.ts
# Utils for implicit intents
#
from IPython import get_ipython

def get_nb_data_info():
    shell = get_ipython()

    run_code = """
    from IPython import get_ipython
    from IPython.core.magics.namespace import NamespaceMagics

    import sys

    _nms = NamespaceMagics()
    _Jupyter = get_ipython()
    _nms.shell = _Jupyter.kernel.shell
    __pd, __lux = None, None

    def _check_imports():
        global __pd, __lux
        
        if 'pandas' in sys.modules:
            import pandas as __pd
        
        if 'lux' in sys.modules:
            import lux as __lux


    def get_colnames(x):
        print('Getting col name for ', x)
        obj = eval(x)
        if __lux and (isinstance(obj, __lux.core.frame.LuxDataFrame) or isinstance(obj, __pd.DataFrame)):
            colnames = list(obj.columns)
        
        elif __lux and (isinstance(obj, __lux.core.series.LuxSeries) or isinstance(obj, __pd.Series)): 
            colnames = [obj.name]
        
        else:
            print('No column names available.')
            colnames = []
        
        print(colnames)
        return colnames

    def keep(v):
        try: 
            obj = eval(v)
            if __pd and __pd is not None and (
                isinstance(obj, __pd.DataFrame)
                or isinstance(obj, __pd.Series)):
                return True

            if __lux and __lux is not None and (
                isinstance(obj, __lux.core.frame.LuxDataFrame)
                or isinstance(obj, __lux.core.series.LuxSeries)):
                # print('is lux')

                return True

            return False

        except Exception as e:
            print('Excepted in keep...', e)
            return False

    def get_dfs_and_columns():
        _check_imports()
        
        all_mods = _nms.who_ls()
        
        d = {_v:get_colnames(_v) for _v in all_mods if keep(_v)}
        
        return d

    get_dfs_and_columns()
    """

    result = shell.run_cell(run_code).result 

    return result