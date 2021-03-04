import ast
from collections import namedtuple
import numpy as np
import pandas as pd

from IPython import get_ipython
from IPython.core.magics.namespace import NamespaceMagics

from lux.implicit.ast_profiler import Analyzer
import lux

CodeTrackerItem = namedtuple("CodeTrackerItem", "exec_order code")

from IPython.core.debugger import set_trace

class CodeTracker():

    def __init__(self):
        
        # state
        self.code_history = []            # list of CodeTrackerItem(exec_count, code_string)
        self.parsed_history = []          # list of CodeHistoryItem(df_name, cols, f_name, f_arg_dict)
        #self.implicit_intent = []
        self.df_info = {}
        self.name_to_id = {}               # df_name: id()
        self.id_to_names = {}              # id(): [df_name, ...], for edge case where multiple vars ref same object 

        self.unanalyzed_code = []

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
            #self.shell.events.register('post_run_cell', self.post_run_cell)
            self.shell.events.register('pre_run_cell', self.pre_run_cell)
        #print("CodeTracker: Shell watching init success.")

    # def pre_run_cell(self, info):
    #     print(f'Pre run cell, code: {info.raw_cell}')
    #     set_trace()

    #     try: 
    #         self.shell.ex(info.raw_cell)
    #         d = self.get_nb_df_info()
        
    #     except Exception as e:
    #         raise # if code fails to run this raises up to normal exception handler

    #     x = 11
    
    def pre_run_cell(self, info):
        """
        Run before each cell is executed. See if valid python and if so add to unanalyzed code
        """
        try: 
            _code_str = info.raw_cell
            ast.parse(_code_str)

            self.unanalyzed_code.append(_code_str)
        except SyntaxError:
            pass
    

    def analyze_recent_code(self):
        if self.unanalyzed_code: # len > 0
            # run analyis code ONLY on new code since last analyze
            code_str = "\n".join(self.unanalyzed_code)
            for s in self.unanalyzed_code:
                self.code_history.append( CodeTrackerItem(self.curr_time, s) )
            
            # clean up
            self.curr_time += 1 # this is actually more of the analysis time than exec time
            self.unanalyzed_code = []

            # run analysis 
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
                    if len(self.signal_weights) > 0:
                        min_new_w = max(self.signal_weights)
                    else:
                        min_new_w = .9
                    num_new_weights = analyzer.history[-1].ex_order + 1 # get the max which will be last
                    code_weights = np.linspace(start = min_new_w, stop = 1, num= num_new_weights)
                
                w0 = [code_weights[i] for i in range(n_new_signals)]
                self.signal_weights = np.append(self.signal_weights, w0) # add new weights for new signals

                # save new signals 
                self.parsed_history.extend( analyzer.history)

                #assert len(self.parsed_history) == len(self.signal_weights)
            
            # set a flag or call something so that the LDFs update and know the implicit recs have changed
            lux.config.update_actions["flag"] = True
    
    def get_all_code(self, time_thresh=0):
        """ returns all the previously executed code as one string """

        _filtered = list(filter(lambda a: a.exec_order >= time_thresh, self.code_history))
        just_strings = [item.code for item in _filtered]
        one_str = "\n".join(just_strings)

        return one_str
    
    def get_implicit_intent(self, df_id):
        """ returns LIST of columns"""
        
        most_recent_signal = None
        col_list = []

        if self.parsed_history and df_id in self.id_to_names:
            df_names = self.id_to_names[df_id]

            # filter to only this df and the weights 
            mask = [item.df_name in df_names for item in self.parsed_history]
            weights = self.signal_weights[mask]
            signals = list(filter(lambda a: a.df_name in df_names, self.parsed_history))

            # get signal and cols over time
            if signals:
                most_recent_signal = signals[-1]
                col_list = self.get_weighted_col_order(signals[:-1], weights)

        return most_recent_signal, col_list
    
    def get_weighted_col_order(self, signals, weights, col_thresh = .25):
        """ 
        Take in list of CodeTrackerItem signals and weights
        Return list of col names sorted from highest to lowest importance
        """
        col_dict = {}

        for s, w in zip(signals, weights):
            cols = s.cols 
            for c in cols:
                if c in col_dict:
                    col_dict[c] += w 
                else:
                    col_dict[c] = w
        
        l = []
        if col_dict:
            l = list(col_dict.items())
            l.sort(key=lambda x: x[1], reverse=True)
            l = [i[0] for i in l if i[1] > col_thresh]
        
        return l

    ###
    ### Utils for getting df and column names from NB 
    ###
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
            return False
    
    def get_name_to_id_map(self, names):
        m = {}
        for n in names:
            m[n] = self.shell.ev(f"id({n})")
        return m
    
    def create_inverse_map(self, d):
        """ take a dict and make reverse map of value: [key_1, key_2,...] """
        _d = {}

        for k,v in d.items():
            if v in _d:
                _d[v].append(k)
            else:
                _d[v] = [k]
        
        return _d

    def get_nb_df_info(self):
        """ 
        Gets the names of dfs and their columns
        code inspo from: https://github.com/lckr/jupyterlab-variableInspector/blob/master/src/inspectorscripts.ts

        returns dict of {df_name: [col_name, ...]}
        """
        d = None
        
        if self.shell:
            # get dfs and cols 
            all_mods = self._nms.who_ls()
            d = {_v:self.get_colnames(_v) for _v in all_mods if self.keep(_v)}
            self.df_info = d

            self.name_to_id = self.get_name_to_id_map(d.keys())
            self.id_to_names = self.create_inverse_map(self.name_to_id)
            
        return d