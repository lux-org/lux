import inspect
import sys
import pickle as pkl
import lux
import autopep8
import math
import os


class LuxTracer:
    def profile_func(self, frame, event, arg):
        # Profile functions should have three arguments: frame, event, and arg.
        # frame is the current stack frame.
        # event is a string: 'call', 'return', 'c_call', 'c_return', or 'c_exception'.
        # arg depends on the event type.
        # See: https://docs.python.org/3/library/sys.html#sys.settrace
        try:
            if event == "line":
                # frame objects are described here: https://docs.python.org/3/library/inspect.html
                fcode = frame.f_code
                line_no = frame.f_lineno
                func_name = fcode.co_name

                includeMod = [
                    os.path.join("lux", "vis"),
                    os.path.join("lux", "vislib"),
                    os.path.join("lux", "executor"),
                ]
                includeFunc = [
                    "add_quotes",
                    "execute",
                    "execute_sampling",
                    "execute_filter",
                    "execute_binning",
                    "execute_scatter",
                    "execute_aggregate",
                    "execute_2D_binning",
                ]
                if any(x in frame.f_code.co_filename for x in includeMod):
                    if (
                        func_name != "<lambda>"
                    ):  # ignore one-liner lambda functions (repeated line events)
                        if any(
                            x in f"{frame.f_code.co_filename}--{func_name}--{line_no}"
                            for x in includeFunc
                        ):
                            lux.config.tracer_relevant_lines.append(
                                [frame.f_code.co_filename, func_name, line_no]
                            )
                            # print(f"{frame.f_code.co_filename}--{func_name}--{line_no}")

        except:
            # pass  # just swallow errors to avoid interference with traced processes
            raise  # for debugging
        return self.profile_func

    def start_tracing(self):
        # print ("-----------start_tracing-----------")
        # Implement python source debugger: https://docs.python.org/3/library/sys.html#sys.settrace
        # setprofile faster than settrace (only go through I/O)
        sys.settrace(self.profile_func)

    def stop_tracing(self):
        # print ("-----------stop_tracing-----------")
        sys.settrace(None)

    def process_executor_code(self, executor_lines):
        selected = {}
        selected_index = {}
        index = 0
        curr_for = ""
        curr_for_len = 0
        in_loop = False
        loop_end = 0
        output = ""
        function_code = ""

        for l in range(0, len(executor_lines)):
            line = executor_lines[l]
            filename = line[0]
            funcname = line[1]
            line_no = line[2] - 1

            codelines = open(filename).readlines()  # TODO: do sharing of file content here
            if funcname not in ["__init__"]:
                code = codelines[line_no]
                ignore_construct = [
                    "if",
                    "elif",
                    "return",
                    "try",
                    "assert",
                    "with",
                ]  # prune out these control flow programming constructs
                ignore_lux_keyword = [
                    "self.code",
                    "self.name",
                    "__init__",
                    "'''",
                    "self.output_type",
                    "message.add_unique",
                    "Large scatterplots detected",
                    "priority=",
                    "for vis in vislist",
                    "for view in view_collection",
                    "execute_aggregate",
                    "execute_binning",
                    "execute_2D_binning",
                ]  # Lux-specific keywords to ignore
                whitelist = ['if clause.attribute != "Record":', "bin_attribute ="]
                ignore = ignore_construct + ignore_lux_keyword
                if not any(construct in code for construct in ignore) or any(
                    construct in code for construct in whitelist
                ):
                    clean_code_line = codelines[line_no].lstrip()
                    code_line = codelines[line_no].replace("    ", "", 2)
                    if clean_code_line.lstrip() not in selected:
                        if "def add_quotes(var_name):" in clean_code_line:
                            clean_code_line = (
                                "def add_quotes(var_name):\n\treturn '\"' + var_name + '\"'\n"
                            )
                            selected[clean_code_line] = index
                            selected_index[index] = clean_code_line.lstrip()
                        else:
                            leading_spaces = len(code_line) - len(code_line.lstrip())
                            num_tabs = math.ceil(leading_spaces / 8)
                            clean_code_line = "\t" * num_tabs + code_line.lstrip()
                            if clean_code_line.lstrip() not in selected:
                                selected_index[index] = clean_code_line
                                selected[clean_code_line.lstrip()] = index
                        index += 1

        curr_executor = lux.config.executor.name
        if curr_executor != "PandasExecutor":
            import_code = "from lux.utils import utils\nfrom lux.executor.SQLExecutor import SQLExecutor\nimport pandas\nimport math\n"
            var_init_code = "tbl = 'insert your LuxSQLTable variable here'\nview = 'insert the name of your Vis object here'\n"
        else:
            import_code = "from lux.utils import utils\nfrom lux.executor.PandasExecutor import PandasExecutor\nimport pandas\nimport math\n"
            var_init_code = "ldf = 'insert your LuxDataFrame variable here'\nvis = 'insert the name of your Vis object here'\nvis._vis_data = ldf\n"
        function_code += "\t" + import_code

        # need to do some preprocessing before we give the code to autopep8 for formatting
        # there are some cases that the formatter does not handle correctly which we need to handle on our own
        prev_line = ""
        for key in selected_index.keys():
            line = selected_index[key]
            line_stripped = line.lstrip()
            leading_spaces = len(line) - len(line_stripped)
            if (
                leading_spaces > 0
                and not prev_line.lstrip().startswith("for")
                and not line_stripped.startswith("attributes.add")
            ):
                leading_spaces = leading_spaces - 1
            if prev_line != "":
                construct_check = prev_line.lstrip().startswith(
                    ("if", "else", "with", "for")
                ) or line_stripped.startswith(("if", "else", "with", "for"))
                prev_leading_spaces = len(prev_line) - len(prev_line.lstrip())

                if not construct_check:
                    if prev_leading_spaces < leading_spaces:
                        leading_spaces = prev_leading_spaces
            if "curr_edge" in line:
                leading_spaces = leading_spaces + 1
            line = "\t" * leading_spaces + line.lstrip()
            function_code += line
            prev_line = line

        if curr_executor != "PandasExecutor":
            output += "def create_chart_data(tbl, view):\n"
            function_code += "\nreturn view._vis_data"
        else:
            output += "def create_chart_data(ldf, vis):\n"
            function_code += "\nreturn vis._vis_data"

        # options = autopep8.parse_args(['--max-line-length', '100000', '-', "--ignore", "E231,E225,E226,E227,E228,E22"])
        # options = autopep8.parse_args(['--max-line-length', '100000', '-', "--ignore", "E101,E128,E211,E22,E27,W191,E231"])
        options = autopep8.parse_args(
            ["--max-line-length", "100000", "-", "--select", "E20,E112,E113,E117"]
        )
        function_code = autopep8.fix_code(function_code, options)

        for line in function_code.split("\n"):
            output += "\t" + line + "\n"
        return output
