import inspect
import sys
import pickle as pkl
import lux

class LuxTracer():            
    def profile_func(self, frame, event, arg):
        #Profile functions should have three arguments: frame, event, and arg. 
        #frame is the current stack frame. 
        #event is a string: 'call', 'return', 'c_call', 'c_return', or 'c_exception'.
        #arg depends on the event type.
        # See: https://docs.python.org/3/library/sys.html#sys.settrace
        try: 
            if event == 'line' :
                #frame objects are described here: https://docs.python.org/3/library/inspect.html
                fcode = frame.f_code             
                line_no = frame.f_lineno
                func_name = fcode.co_name
                #includeMod = ['lux/vis', 'lux/action', 'lux/vislib', 'lux/executor', 'lux/interestingness']
                includeMod = ['lux\\vis', 'lux\\vislib', 'lux\\executor']
                includeFunc = ['execute_sampling', 'execute_filter', 'execute_binning', 'execute_scatter', 'execute_aggregate', 'execute_2D_binning', 'create_where_clause']
                if any(x in frame.f_code.co_filename for x in includeMod):
                    if (func_name!="<lambda>"): #ignore one-liner lambda functions (repeated line events)
                        if any(x in f"{frame.f_code.co_filename}--{func_name}--{line_no}" for x in includeFunc):
                            lux.config.tracer_relevant_lines.append([frame.f_code.co_filename,func_name,line_no])
                            #print(f"{frame.f_code.co_filename}--{func_name}--{line_no}")
                    
        except:
            # pass  # just swallow errors to avoid interference with traced processes
            raise  # for debugging
        return self.profile_func

    def start_tracing(self):
        #print ("-----------start_tracing-----------")
        # Implement python source debugger: https://docs.python.org/3/library/sys.html#sys.settrace
        # setprofile faster than settrace (only go through I/O)
        sys.settrace(self.profile_func) 

    def stop_tracing(self):
        #print ("-----------stop_tracing-----------")
        sys.settrace(None) 


    def process_executor_code(self,executor_lines):
        selected = {}
        selected_index = {}
        index = 0
        curr_for = ""
        curr_for_len = 0
        in_loop = False
        loop_end = 0
        output = ""

        for l in range(0, len(executor_lines)):
            line = executor_lines[l]
            filename = line[0]
            funcname = line[1]
            line_no = line[2]-1
            
            codelines = open(filename).readlines()# TODO: do sharing of file content here
            if (funcname not in ['__init__']):
                code = codelines[line_no]
                ignore_construct = ['if','elif','return'] # prune out these control flow programming constructs                    
                ignore_lux_keyword = ['self.code','self.name','__init__','PandasExecutor.',"'''",'self.output_type', 'message.add_unique', 'Large scatterplots detected', 'priority=']# Lux-specific keywords to ignore
                ignore = ignore_construct+ignore_lux_keyword
                if not any(construct in code for construct in ignore):
                    #need to handle for loops, this keeps track of when a for loop shows up and when the for loop code is repeated
                    clean_code_line = codelines[line_no].lstrip()
                    if clean_code_line not in selected:
                        selected[clean_code_line] = index
                        selected_index[index] = codelines[line_no].replace("    ", "", 1)
                        index += 1
        for key in selected_index.keys():
            output += selected_index[key]
        return(output)