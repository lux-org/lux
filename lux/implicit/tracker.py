import ast
from collections import namedtuple
import numpy as np
import pandas as pd

from IPython import get_ipython
from IPython.core.magics.namespace import NamespaceMagics

from lux.implicit.ast_profiler import Analyzer
import lux

CodeTrackerItem = namedtuple("CodeTrackerItem", "exec_order code")

# from IPython.core.debugger import set_trace

class CodeTracker():

    def __init__(self):
        
        # state
        self.code_history = []            # list of CodeTrackerItem(exec_count, code_string)
        self.parsed_history = []          # list of CodeHistoryItem(df_name, cols, f_name, f_arg_dict)
        #self.implicit_intent = []
        self.df_info = {}
        self.getting_info_flag = False

        # inits
        self.shell = get_ipython()
        self.init_watching()
        self.curr_time = 0
        self.signal_weights = np.array([])
        self.time_decay = 0.9

        self._nms = NamespaceMagics()
        self._nms.shell = self.shell #.kernel.shell
        
    
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
            # could use result.execution_count maybe as well
            self.code_history.append( CodeTrackerItem(self.curr_time, result.info.raw_cell) )

            # run analyis code ONLY on new code
            code_str = result.info.raw_cell
            tree = ast.parse(code_str) # self.get_all_code()
            name_dict = self.get_nb_df_info()
            analyzer = Analyzer(name_dict, code_str)
            analyzer.visit(tree)

            # update weights
            n_new_signals = len(analyzer.history)

            if n_new_signals > 0:
                self.signal_weights *= self.time_decay
                
                if n_new_signals == 1:
                    code_weights = [1]
                else:
                    if self.signal_weights:
                        min_new_w = max(self.signal_weights)
                    else:
                        min_new_w = .9
                    num_new_weights = analyzer.history[-1].ex_order + 1 # get the max which will be last
                    code_weights = np.linspace(start = min_new_w, stop = 1, num= num_new_weights)
                
                w0 = [code_weights[item.ex_order] for item in analyzer.history]
                self.signal_weights = np.append(self.signal_weights, w0) # add new weights for new signals

                # save new signals 
                self.parsed_history.extend( analyzer.history)

                assert len(self.parsed_history) == len(self.signal_weights)
            
            # clean up
            self.getting_info_flag = False
            # set a flag or call something so that the LDFs update and know the implicit recs have changed
            lux.config.update_actions["flag"] = True
    
    def get_all_code(self, time_thresh=0):
        """ returns all the previously executed code as one string """

        _filtered = list(filter(lambda a: a.exec_order >= time_thresh, self.code_history))
        just_strings = [item.code for item in _filtered]
        one_str = "\n".join(just_strings)

        return one_str
    
    def get_implicit_intent(self, f_df_name):
        """ returns LIST of columns"""
        # TODO aggregate time here or make it just cleaner?
        # TODO maybe need to use id here instead of name
        
        if self.parsed_history:

            # filter to only this df and the weights 
            mask = [item.df_name == f_df_name for item in self.parsed_history]
            weights = self.signal_weights[mask]
            signals = list(filter(lambda a: a.df_name == f_df_name, self.parsed_history))

            order = np.argsort(-1 * weights) # order so that highest is first 

            l = []
            for i in order:
                l.append(signals[i])
            
            return signals 

            # generate 
            # cols = []
            # if f_df_name not in self.df_info:
            #     self.get_nb_df_info()
            
            # if f_df_name in self.df_info:
            #     cols = self.df_info[f_df_name]
            
            # col_totals = {}
            # for c in cols: 
            #     _total = 0
            #     for s, w in zip(signals, weights):
            #         if c in s.cols:
            #             _total += w 


    def get_colnames(self, x):
        obj = self.shell.ev(x)
        if isinstance(obj, lux.core.frame.LuxDataFrame) or isinstance(obj, pd.DataFrame):
            colnames = list(obj.columns)
        elif isinstance(obj, lux.core.series.LuxSeries) or isinstance(obj, pd.Series): 
            colnames = [obj.name]
        else:
            colnames = []
        return colnames

    def keep(self, v):
        try: 
            obj = self.shell.ev(v)
            if isinstance(obj, pd.DataFrame) or isinstance(obj, pd.Series):
                return True
            if isinstance(obj, lux.core.frame.LuxDataFrame) or isinstance(obj, lux.core.series.LuxSeries):
                return True
            return False
        except Exception as e:
            #print('Excepted in keep...', e)
            return False

    def get_nb_df_info(self):
        """ 
        Gets the names of dfs and their columns
        code inspo from: https://github.com/lckr/jupyterlab-variableInspector/blob/master/src/inspectorscripts.ts

        returns dict of {df_name: [col_name, ...]}
        """
        self.getting_info_flag = True
        d = None
        
        if self.shell:
            # get dfs and cols 
            all_mods = self._nms.who_ls()
            d = {_v:self.get_colnames(_v) for _v in all_mods if self.keep(_v)}
            self.df_info = d
            
        return d