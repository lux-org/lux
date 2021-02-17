from IPython import get_ipython
from lux.implicit.profiler import get_recent_funcs_cols
import lux

class CodeTracker():

    def __init__(self):
        
        # state
        self.code_history = []              # list of tuples (exec_count, code_string)
        self.f_calls = [("", [""], "")]     # (df_name, [cols], func_name)
        self.col_refs = {}                  # {col_name: num_refs}
        #self.implicit_intent = []
        self.df_info = {}
        self.getting_info_flag = False

        # inits
        self.shell = get_ipython()
        self.init_watching()
    
    def init_watching(self):
        """
        Start watching. For more info: https://ipython.readthedocs.io/en/stable/config/callbacks.html
        """
        if self.shell:
            self.shell.events.register('post_run_cell', self.post_run_cell)
        #print("CodeTracker: Shell watching init success.")

    def post_run_cell(self, result):
        """
        Run each time a jupyter cell is executed
        
        result.success: flag if execution errored
        result.info.raw_cell: code that user ran
        """

        if result.success and not self.getting_info_flag:
            self.code_history.append( (result.execution_count, result.info.raw_cell) )

            # run analyis code
            f_calls, col_refs = get_recent_funcs_cols(self.get_all_code(), self.get_nb_df_info())
            self.f_calls = f_calls
            self.col_refs = col_refs
            self.getting_info_flag = False

            # TODO set a flag or call something so that the LDFs update and know the implicit recs have changed
            lux.config.update_actions["flag"] = True
    
    def get_all_code(self):
        """ returns all the previously executed code as one string """

        just_strings = [c[1] for c in self.code_history]
        one_str = "\n".join(just_strings)

        return one_str
    
    def get_implicit_intent(self, df_name=None):
        """ returns LIST of columns"""
        # TODO incorporate time decay notion here where decreased with each subsequent cell execution
        # can return tuples of (col_name, score) to send to lux and have ranking of vis
        
        if self.col_refs:
            _cols = list(self.col_refs.items())

            if df_name and (df_name in self.df_info): # filter to only cols from this df
                _this_df_cols = self.df_info[df_name]
                _cols = [item for item in _cols if (item[0] in _this_df_cols)]

            _cols.sort(key=lambda tup: tup[1], reverse=True)
            trimmed_cols = [i[0] for i in _cols]

            return trimmed_cols


    # TODO does this really need to be run every time? Maybe can store when 
    # BUG this prints out the result to the user's notebook which is annoying since it has to be read too..
    def get_nb_df_info(self):
        """ 
        Gets the names of dfs and their columns
        code inspo from: https://github.com/lckr/jupyterlab-variableInspector/blob/master/src/inspectorscripts.ts

        returns dict of {df_name: [col_name, ...]}
        """
        self.getting_info_flag = True

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
            #print('Getting col name for ', x)
            obj = eval(x)
            if __lux and (isinstance(obj, __lux.core.frame.LuxDataFrame) or isinstance(obj, __pd.DataFrame)):
                colnames = list(obj.columns)
            
            elif __lux and (isinstance(obj, __lux.core.series.LuxSeries) or isinstance(obj, __pd.Series)): 
                colnames = [obj.name]
            
            else:
                #print('No column names available.')
                colnames = []
            
            #print(colnames)
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

                    return True

                return False

            except Exception as e:
                #print('Excepted in keep...', e)
                return False

        def get_dfs_and_columns():
            _check_imports()
            
            all_mods = _nms.who_ls()
            
            d = {_v:get_colnames(_v) for _v in all_mods if keep(_v)}
            
            return d

        get_dfs_and_columns()
        """
        if self.shell:
            result = self.shell.run_cell(run_code).result 
            self.df_info = result
        else:
            result = None 
            
        return result
    
    
