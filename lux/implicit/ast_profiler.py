import numpy as np
import ast 
from collections import namedtuple

CodeHistoryItem = namedtuple("CodeHistoryItem", "df_name cols f_name f_arg_dict ex_order code_str")
ColFilter = namedtuple("ColFilter", "df_name col_name comp val")

# from IPython.core.debugger import set_trace

class Analyzer(ast.NodeVisitor):
    def __init__(self, df_meta, code_str):
        """
        df_meta: DICT 
            Names of all lux df objects in the user's session
            {"df_name": set([cols])}
        """
        self.df_meta = df_meta
        # make sure the cols are sets 
        for k in df_meta.keys():
            df_meta[k] = set(df_meta[k])
        self.func_kws = ["value_counts", "unique", "crosstab", "describe",  "query", "groupby", "agg", "filter", "loc"] # do I want drop here?
        self.history = []
        self.ex_count = 0
        self.code_str_tokens = code_str.split("\n")

    ####
    #### Override NodeVisitor funcs to handle types of nodes ####
    ####
    def visit_FunctionDef(self, node):
        pass
    
    def visit_Attribute(self, node):
        self.handle_attr_or_subs(node)
        self.ex_count += 1
        
    def visit_Subscript(self, node):
        self.handle_attr_or_subs(node)
        self.ex_count += 1
        
    def visit_Call(self, node):
        self.handle_call(node)
        self.ex_count += 1
        #self.generic_visit(node)
    
    def visit_Assign(self, node):
        self.handle_assign(node)
        self.ex_count += 1
        #self.generic_visit(node)
    
    ####
    #### Main parsing logic ####
    ####
    def handle_assign(self, node):
        all_t = {}
        v = node.value

        this_h = []
        call_h = []
        
        # get targets that are dfs
        for t in node.targets:
            df_name, cols, _ = self.get_df_col(t)
            self.dict_add_extend(all_t, df_name, cols)
        
        # parse value 
        if type(v) == ast.BinOp:
            left_df, left_cols, _ = self.get_df_col(v.left)
            right_df, right_cols, _ = self.get_df_col(v.right)
            self.dict_add_extend(all_t, left_df, left_cols)
            self.dict_add_extend(all_t, right_df, right_cols)

        elif type(v) == ast.Call:
            call_h = self.handle_call(v, lh=False) # send call to history and just record cols here later
        
        elif type(v) == ast.Subscript:
            call_h = self.handle_attr_or_subs(v, lh=False)
                
        for df_key, col_list in all_t.items():
            if df_key in self.df_meta:
                _f_name = ""
                _f_args = {}

                if call_h:
                    for hist_item in call_h:
                        this_c = col_list.extend(hist_item.cols)
                        if hist_item.f_name:
                            _f_name = hist_item.f_name
                            _f_args = hist_item.f_arg_dict

                        this_c = list(self.df_meta[df_key].intersection(col_list))

                        if hist_item.df_name != df_key:
                            h = CodeHistoryItem(df_key, this_c, _f_name, _f_args, self.ex_count, self.get_code_string(node))
                            this_h.append(h)
                else:
                    this_c = list(self.df_meta[df_key].intersection(col_list))
                    h = CodeHistoryItem(df_key, this_c, _f_name, _f_args, self.ex_count, self.get_code_string(node))
                    this_h.append(h)
        
        self.add_to_history(call_h + this_h)

    def handle_attr_or_subs(self, node, lh=True):
        """
        df[]
        df.A

        """
        df_name, cols, filts = self.get_df_col(node) # TODO handle the filt
        this_h = []

        if df_name in self.df_meta:       
            cols = list(self.df_meta[df_name].intersection(cols)) 
            
            if filts: 
                h = CodeHistoryItem(df_name, cols, "subs_filter", {"filts": filts}, self.ex_count, self.get_code_string(node))
            else:
                h = CodeHistoryItem(df_name, cols, "", {}, self.ex_count, self.get_code_string(node))
            this_h.append(h)
        
        if lh:
            self.add_to_history(this_h)

        return this_h
    
    def handle_call(self, call_node, lh=True):        
        this_h = []
        # only looks at df.call, not call()
        if type(call_node.func) == ast.Attribute or ( 
             (type(call_node.func) == ast.Name) and (self.parse_value(call_node.func) == "crosstab") ):

            cols = []
            df_name = ""
            df_s = {}

            if type(call_node.func) == ast.Attribute:
                v = call_node.func.value

                if type(v) == ast.Call: # for df.groupby().agg     "df_name cols f_name f_arg_dict"
                    h = self.handle_call(v, lh=False)[0]

                    df_name = h.df_name
                    # func_name = f"{h.f_name}.{call_node.func.attr}" # leads to groupby.agg which isnt in approved list
                    func_name = h.f_name # 
                    cols = h.cols
                else:
                    func_name = call_node.func.attr
                    df_name, cols, _ = self.get_df_col(v)
            
            else: # crosstab() case
                func_name = "crosstab"
                df_name = "pd"
                
            arg_dict, df_s = self.parse_call_args(call_node, df_name)

            # only append for functions im interested in
            if func_name in self.func_kws:
                # make sure call args are columns before adding 
                if df_name in df_s and df_name in self.df_meta:
                    _new_c = df_s[df_name]
                    cols.extend(self.df_meta[df_name].intersection(_new_c) )
                    cols = list(np.unique(cols))
                    del df_s[df_name]

                # special case for query since the columns are in the filter, may be able to pass this filter to lux intent
                if func_name == "query" and "args" in arg_dict:
                    query_param = arg_dict["args"][0]
                    cols = [s for s in query_param.split() if s in self.df_meta[df_name]]
                
                h = CodeHistoryItem(df_name, cols, func_name, arg_dict, self.ex_count, self.get_code_string(call_node))
                this_h.append(h)
                
                # if other columns are referenced in df_s that are not in df_name 
                for _other_df, _other_c in df_s.items():
                    if _other_df in self.df_meta:
                        this_c = list(self.df_meta[_other_df].intersection(_other_c))
                        h = CodeHistoryItem(_other_df, this_c, func_name, arg_dict, self.ex_count, self.get_code_string(call_node))
                        this_h.append(h)
        if lh:
            self.add_to_history(this_h)

        return this_h
        
       
    def parse_call_args(self, call_node, df_name = ""):
        """
        Parse args to function. If these args are column names then group them by the df and return this dict
        """
        # get args and kw args from node
        arg_dict = {}

        args = []
        df_s = {}
        for a in call_node.args:
            if (type(a) == ast.Attribute) or (type(a) == ast.Subscript):
                df_name, cols, _ = self.get_df_col(a)
                
                # assign to df dict
                self.dict_add_extend(df_s, df_name, cols)
                
                args.append(df_name)
                args.extend(cols)
            elif type(a) == ast.Dict:
                d_keys, d_values = self.parse_dict(a)

                all_items = []
                all_items.extend(d_keys)
                for item_arr in d_values:
                    all_items.extend(item_arr)
                
                if df_name:
                    df_s[df_name] = all_items

                args.extend(all_items)
            else:
                v = self.parse_value(a)
                if v:
                    if type(v) == str: v = [v]
                    args.extend(v)
                    if df_name:
                        df_s[df_name] = v
        
        if args:
            arg_dict["args"] = args

        for kw in call_node.keywords:
            kw_arg = kw.arg
            kw_v = self.parse_value(kw.value)
            arg_dict[kw_arg] = kw_v        
        
        return arg_dict, df_s
    
    ####
    #### Utils funcs for parsing data from nodes 
    ####
    def parse_dict(self, node):
        if type(node) != ast.Dict: return 

        keys = self.parse_value(node.keys)
        values = self.parse_value(node.values)

        return keys, values

    def get_df_col(self, v):
        df_name = ""
        cols = []
        filts = None

        if type(v) == ast.Attribute:
            df_name, cols = self.attr_to_str(v)
        elif type(v) == ast.Subscript:
            df_name, cols, filts = self.subs_to_str(v)
        elif self.parse_value(v):
            df_name = self.parse_value(v)
        
        if type(cols) == str: cols = [cols]

        return df_name, cols, filts
            
    def attr_to_str(self, attr_node):
        if type(attr_node) != ast.Attribute: return
            
        v_str = self.parse_value(attr_node.value)
        a_str = attr_node.attr
        
        return v_str, a_str

    def subs_to_str(self, subs_node):
        """
        Parses subscript. For filters, works up to two compares. If three like df[() & () & ()] will not work rn
        """
        if type(subs_node) != ast.Subscript: return
        
        cols = []
        df_name, cols, _ = self.get_df_col(subs_node.value) # if .loc then _ will be loc
        filt = None
        
        if type(subs_node.slice) == ast.Compare: # FILTER
            d, filt = self.parse_compare(subs_node.slice)
            if type(filt) != list: filt = [filt]
            cols.extend(d[df_name]) # NOTE ignoring the case where inner compare is different like df_A[df_B.col > 1]
        
        elif (type(subs_node.slice) == ast.BinOp) & (type(subs_node.slice.left) == ast.Compare) & (type(subs_node.slice.right) == ast.Compare): # Filter df[(left) & (right)]
            # TODO turn this into recusive function to parse var length expressions
            d_l, filt_l = self.parse_compare(subs_node.slice.left)
            d_r, filt_r = self.parse_compare(subs_node.slice.right)

            op = ""

            if type(subs_node.slice.op) == ast.BitAnd:
                op = "&"
            elif type(subs_node.slice.op) == ast.BitOr:
                op = "|"

            cols.extend(d_l[df_name] + d_r[df_name]) # NOTE once again assuming inner compare is from same df
            filt = [filt_l, op,  filt_r]

        else: # slice will be constant or name if single item
            _cols = self.parse_value(subs_node.slice)
            if not cols: cols = []
            else: cols.extend(_cols)
        
        return df_name, cols, filt

    # TODO this will always be a filter I think...
    # ColFilter = namedtuple("ColFilter", "df_name col_name comp val")

    def parse_compare(self, comp_node):
        """
        return d of col and df refs and ColFilter of the filter operations
        """
        if type(comp_node) != ast.Compare: return
        df, cols, _ = self.get_df_col(comp_node.left)
        d = {df: cols}

        # cv, _, _ = self.get_df_col(comp_node.comparators[0])
        cv = self.parse_value(comp_node.comparators[0])
        
        op = comp_node.ops[0]
        comp = ""
        
        if type(op) == ast.Eq:
            comp = "=="
        elif type(op) == ast.NotEq:
            comp = "!="
        elif type(op) == ast.Lt:
            comp = "<"
        elif type(op) == ast.LtE:
            comp = "<="
        elif type(op) == ast.Gt:
            comp = ">"
        elif type(op) == ast.GtE:
            comp = ">="
        
        # also ast.Is, ast.IsNot, ast.In, ast.NotIn
        
        filt = ColFilter(df, cols[0], comp, cv)
        
        return d, filt
        
    def parse_value(self, v_node):
        if type(v_node) == ast.Name:
            return v_node.id
        
        if type(v_node) == ast.Starred:
            return self.parse_value(v_node.value)
        
        if type(v_node) == ast.Constant:
            return v_node.value
        
#         if type(v_node) == ast.Slice:
#             return self.parse_value(v_node.lower), self.parse_value(v_node.upper)
        
        if (type(v_node) == ast.List) or (type(v_node) == ast.Tuple):
            str_list = []
            for item in v_node.elts:
                str_list.append(self.parse_value(item))
            
            return str_list
        
        if type(v_node) == list or type(v_node) == tuple:
            str_list = []
            for item in v_node:
                str_list.append(self.parse_value(item))
            
            return str_list
    
    ####
    #### Utils funcs for state management etc
    ####

    def dict_add_extend(self, dict_name, key, vals): 
        if key in dict_name:
            dict_name[key].extend(vals)
        else:
            dict_name[key] = vals
    
    def add_to_history(self, h_items):
        if type(h_items) != list:
            h_items = [h_items]
        
        # only add items that have columns or a function reference
        for h in h_items:
            if h.df_name and (h.cols or h.f_name):
                self.history.extend([h]) 
    
    def get_code_string(self, node):
        code_s = ""
        if len(self.code_str_tokens) > node.lineno - 1:
            code_s = self.code_str_tokens[node.lineno - 1]
        
        return code_s