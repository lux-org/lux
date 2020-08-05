import pandas as pd
from lux.vis.Clause import Clause
from lux.vis.Vis import Vis
from lux.vis.VisList import VisList
from lux.utils.utils import check_import_lux_widget
#import for benchmarking
import time
import typing
import warnings
class LuxDataFrame(pd.DataFrame):
    '''
    A subclass of pd.DataFrame that supports all dataframe operations while housing other variables and functions for generating visual recommendations.
    '''
    # MUST register here for new properties!!
    _metadata = ['_intent','data_type_lookup','data_type',
                 'data_model_lookup','data_model','unique_values','cardinality',
                'min_max','plot_config', 'current_vis','_widget', '_rec_info', 'recommendation']

    def __init__(self,*args, **kw):
        from lux.executor.PandasExecutor import PandasExecutor
        self._intent = []
        self._rec_info=[]
        self.recommendation = {}
        self.current_vis = []
        super(LuxDataFrame, self).__init__(*args, **kw)

        if (len(self)>0): #only compute metadata information if the dataframe is non-empty
            self.compute_stats()
            self.compute_dataset_metadata()
            self.infer_structure()

        self.executor_type = "Pandas"
        self.executor = PandasExecutor
        self.SQLconnection = ""
        self.table_name = ""

        self.default_pandas_display = True
        self.toggle_pandas_display = True
        self.toggle_benchmarking = False
        self.plot_config = None

    @property
    def _constructor(self):
        return LuxDataFrame
    
    def set_default_display(self, type:str) -> None:
        """
        Set the widget display to show Pandas by default or Lux by default
        Parameters
        ----------
        type : str
            Default display type, can take either the string `lux` or `pandas` (regardless of capitalization)
        """        
        if (type.lower()=="lux"):
            self.default_pandas_display = False
        elif (type.lower()=="pandas"):
            self.default_pandas_display = True
        else: 
            warnings.warn("Unsupported display type. Default display option should either be `lux` or `pandas`.",stacklevel=2)
    def infer_structure(self):
        # If the dataframe is very small and the index column is not a range index, then it is likely that this is an aggregated data
        is_multi_index_flag = self.index.nlevels !=1
        not_int_index_flag = self.index.dtype !='int64'
        small_df_flag = len(self)<100
        self.pre_aggregated = (is_multi_index_flag or not_int_index_flag) and small_df_flag 
    def set_executor_type(self, exe):
        if (exe =="SQL"):
            import pkgutil
            if (pkgutil.find_loader("psycopg2") is None):
                raise ImportError("psycopg2 is not installed. Run `pip install psycopg2' to install psycopg2 to enable the Postgres connection.")
            else:
                import psycopg2
            from lux.executor.SQLExecutor import SQLExecutor
            self.executor = SQLExecutor
        else:
            from lux.executor.PandasExecutor import PandasExecutor
            self.executor = PandasExecutor
        self.executor_type = exe
    def set_plot_config(self,config_func:typing.Callable):
        """
        Modify plot aesthetic settings to all visualizations in the dataframe display
        Currently only supported for Altair visualizations
        Parameters
        ----------
        config_func : typing.Callable
            A function that takes in an AltairChart (https://altair-viz.github.io/user_guide/generated/toplevel/altair.Chart.html) as input and returns an AltairChart as output
        
        Example
        ----------
        Changing the color of marks and adding a title for all charts displayed for this dataframe
        >>> df = pd.read_csv("lux/data/car.csv")
        >>> def changeColorAddTitle(chart):
                chart = chart.configure_mark(color="red") # change mark color to red
                chart.title = "Custom Title" # add title to chart
                return chart
        >>> df.set_plot_config(changeColorAddTitle)
        >>> df
        Change the opacity of all scatterplots displayed for this dataframe
        >>> df = pd.read_csv("lux/data/olympic.csv")
        >>> def changeOpacityScatterOnly(chart):
                if chart.mark=='circle':
                    chart = chart.configure_mark(opacity=0.1) # lower opacity
                return chart
        >>> df.set_plot_config(changeOpacityScatterOnly)
        >>> df
        """        
        self.plot_config = config_func
    def clear_plot_config(self):
        self.plot_config = None
    def _refresh_intent(self):
        from lux.compiler.Validator import Validator
        from lux.compiler.Compiler import Compiler
        from lux.compiler.Parser import Parser

        if self.SQLconnection == "":
            self.compute_stats()
            self.compute_dataset_metadata()
        self._intent = Parser.parse(self.get_intent())
        Validator.validate_spec(self._intent,self)
        self.current_vis = Compiler.compile(self, self._intent, self.current_vis)
    def get_intent(self):
        return self._intent
    def set_intent(self, intent:typing.List[typing.Union[str, Clause]]):
        """
        Main function to set the intent of the dataframe.
        The intent input goes through the parser, so that the string inputs are parsed into a lux.Clause object.

        Parameters
        ----------
        intent : typing.List[str,Clause]
            intent list, can be a mix of string shorthand or a lux.Clause object

        Notes
        -----
            :doc:`../guide/clause`
        """        
        self._intent = intent
        self._refresh_intent()
    def copy_intent(self):
        #creates a true copy of the dataframe's intent
        output = []
        for clause in self._intent:
            temp_clause = clause.copy_clause()
            output.append(temp_clause)
        return(output)

    def set_intent_as_vis(self,vis:Vis):
        """
        Set intent of the dataframe as the Vis

        Parameters
        ----------
        vis : Vis
        """        
        self._intent = vis._inferred_intent
        self._refresh_intent()
    def clear_intent(self):
        self._intent = []
        self.current_vis = []
    def to_pandas(self):
        import lux.luxDataFrame
        return lux.luxDataFrame.originalDF(self,copy=False)
    def add_to_intent(self,intent): 
        self._intent.extend(intent)
    def __repr__(self):
        # TODO: _repr_ gets called from _repr_html, need to get rid of this call
        return ""
    def __setitem__(self, key, value):
        super(LuxDataFrame, self).__setitem__(key, value)
        self.compute_stats()
        self.compute_dataset_metadata()
    #######################################################
    ############ Metadata: data type, model #############
    #######################################################
    def compute_dataset_metadata(self):
        self.data_type_lookup = {}
        self.data_type = {}
        self.compute_data_type()
        self.data_model_lookup = {}
        self.data_model = {}
        self.compute_data_model()

    def compute_data_type(self):
        for attr in list(self.columns):
            #TODO: Think about dropping NaN values
            if str(attr).lower() in ["month", "year"]:
                self.data_type_lookup[attr] = "temporal"
            elif self.dtypes[attr] == "float64":
                self.data_type_lookup[attr] = "quantitative"
            elif self.dtypes[attr] == "int64":
                # See if integer value is quantitative or nominal by checking if the ratio of cardinality/data size is less than 0.4 and if there are less than 10 unique values
                if self.cardinality[attr]/len(self) < 0.4 and self.cardinality[attr]<10: 
                    self.data_type_lookup[attr] = "nominal"
                else:
                    self.data_type_lookup[attr] = "quantitative"
            # Eliminate this clause because a single NaN value can cause the dtype to be object
            elif self.dtypes[attr] == "object":
                self.data_type_lookup[attr] = "nominal"
            elif pd.api.types.is_datetime64_any_dtype(self.dtypes[attr]) or pd.api.types.is_period_dtype(self.dtypes[attr]): #check if attribute is any type of datetime dtype
                self.data_type_lookup[attr] = "temporal"
        # for attr in list(df.dtypes[df.dtypes=="int64"].keys()):
        # 	if self.cardinality[attr]>50:
        if (self.index.dtype !='int64' and self.index.name):
            self.data_type_lookup[self.index.name] = "nominal"
        self.data_type = self.mapping(self.data_type_lookup)
    def compute_data_model(self):
        self.data_model = {
            "measure": self.data_type["quantitative"],
            "dimension": self.data_type["ordinal"] + self.data_type["nominal"] + self.data_type["temporal"]
        }
        self.data_model_lookup = self.reverseMapping(self.data_model)

    def mapping(self, rmap):
        group_map = {}
        for val in ["quantitative", "ordinal", "nominal", "temporal"]:
            group_map[val] = list(filter(lambda x: rmap[x] == val, rmap))
        return group_map


    def reverseMapping(self, map):
        reverse_map = {}
        for valKey in map:
            for val in map[valKey]:
                reverse_map[val] = valKey
        return reverse_map

    def compute_stats(self):
        # precompute statistics
        self.unique_values = {}
        self.min_max = {}
        self.cardinality = {}

        for attribute in self.columns:
            if self.dtypes[attribute] != "float64":# and not pd.api.types.is_datetime64_ns_dtype(self.dtypes[attribute]):
                self.unique_values[attribute] = list(self[attribute].unique())
                self.cardinality[attribute] = len(self.unique_values[attribute])
            else:
                self.cardinality[attribute] = 999 # special value for non-numeric attribute
            if self.dtypes[attribute] == "float64" or self.dtypes[attribute] == "int64":
                self.min_max[attribute] = (self[attribute].min(), self[attribute].max())
        if (self.index.dtype !='int64'):
            index_column_name = self.index.name
            self.unique_values[index_column_name] = list(self.index)
            self.cardinality[index_column_name] = len(self.index)
    #######################################################
    ########## SQL Metadata, type, model schema ###########
    #######################################################

    def set_SQL_connection(self, connection, t_name):
        #for benchmarking
        if self.toggle_benchmarking == True:
            tic = time.perf_counter()
        self.SQLconnection = connection
        self.table_name = t_name
        self.compute_SQL_dataset_metadata()
        if self.toggle_benchmarking == True:
            toc = time.perf_counter()
            print(f"Extracted Metadata from SQL Database in {toc - tic:0.4f} seconds")
        self.set_executor_type("SQL")

    def compute_SQL_dataset_metadata(self):
        self.get_SQL_attributes()
        for attr in list(self.columns):
            self[attr] = None
        self.data_type_lookup = {}
        self.data_type = {}
        #####NOTE: since we aren't expecting users to do much data processing with the SQL database, should we just keep this 
        #####      in the initialization and do it just once
        self.compute_SQL_data_type()
        self.compute_SQL_stats()
        self.data_model_lookup = {}
        self.data_model = {}
        self.compute_data_model()

    def compute_SQL_stats(self):
        # precompute statistics
        self.unique_values = {}
        self.min_max = {}

        self.get_SQL_unique_values()
        #self.get_SQL_cardinality()
        for attribute in self.columns:
            if self.data_type_lookup[attribute] == 'quantitative':
                self.min_max[attribute] = (self[attribute].min(), self[attribute].max())

    def get_SQL_attributes(self):
        if "." in self.table_name:
            table_name = self.table_name[self.table_name.index(".")+1:]
        else:
            table_name = self.table_name
        attr_query = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = '{}'".format(table_name)
        attributes = list(pd.read_sql(attr_query, self.SQLconnection)['column_name'])
        for attr in attributes:
            self[attr] = None

    def get_SQL_cardinality(self):
        cardinality = {}
        for attr in list(self.columns):
            card_query = pd.read_sql("SELECT Count(Distinct({})) FROM {}".format(attr, self.table_name), self.SQLconnection)
            cardinality[attr] = list(card_query["count"])[0]
        self.cardinality = cardinality

    def get_SQL_unique_values(self):
        unique_vals = {}
        for attr in list(self.columns):
            unique_query = pd.read_sql("SELECT Distinct({}) FROM {}".format(attr, self.table_name), self.SQLconnection)
            unique_vals[attr] = list(unique_query[attr])
        self.unique_values = unique_vals

    def compute_SQL_data_type(self):
        data_type_lookup = {}
        sql_dtypes = {}
        self.get_SQL_cardinality()
        if "." in self.table_name:
            table_name = self.table_name[self.table_name.index(".")+1:]
        else:
            table_name = self.table_name
        #get the data types of the attributes in the SQL table
        for attr in list(self.columns):
            datatype_query = "SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}' AND COLUMN_NAME = '{}'".format(table_name, attr)
            datatype = list(pd.read_sql(datatype_query, self.SQLconnection)['data_type'])[0]
            sql_dtypes[attr] = datatype

        data_type = {"quantitative":[], "ordinal":[], "nominal":[], "temporal":[]}
        for attr in list(self.columns):
            if str(attr).lower() in ["month", "year"]:
                data_type_lookup[attr] = "temporal"
                data_type["temporal"].append(attr)
            elif sql_dtypes[attr] in ["character", "character varying", "boolean", "uuid", "text"]:
                data_type_lookup[attr] = "nominal"
                data_type["nominal"].append(attr)
            elif sql_dtypes[attr] in ["integer", "real", "smallint", "smallserial", "serial"]:
                if self.cardinality[attr] < 13:
                    data_type_lookup[attr] = "nominal"
                    data_type["nominal"].append(attr)
                else:
                    data_type_lookup[attr] = "quantitative"
                    data_type["quantitative"].append(attr)
            elif "time" in sql_dtypes[attr] or "date" in sql_dtypes[attr]:
                data_type_lookup[attr] = "temporal"
                data_type["temporal"].append(attr)
        self.data_type_lookup = data_type_lookup
        self.data_type = data_type
    def _append_recInfo(self,recommendations:typing.Dict):
        if (recommendations["collection"] is not None and len(recommendations["collection"])>0):
            self._rec_info.append(recommendations)
    def show_more(self):
        from lux.action.custom import custom
        from lux.action.correlation import correlation
        from lux.action.univariate import univariate
        from lux.action.enhance import enhance
        from lux.action.filter import filter
        from lux.action.generalize import generalize
        from lux.action.row_group import row_group
        from lux.action.column_group import column_group

        self._rec_info = []
        if (self.pre_aggregated):
            if (self.columns.name is not None):
                self._append_recInfo(row_group(self))
            if (self.index.name is not None):
                self._append_recInfo(column_group(self))
        else:
            if (self.current_vis is None):
                no_vis = True
                one_current_vis = False
                multiple_current_vis = False
            else:
                no_vis = len(self.current_vis) == 0
                one_current_vis = len(self.current_vis) == 1
                multiple_current_vis = len(self.current_vis) > 1

            if (no_vis):
                self._append_recInfo(correlation(self))
                self._append_recInfo(univariate(self,"quantitative"))
                self._append_recInfo(univariate(self,"nominal"))
                self._append_recInfo(univariate(self,"temporal"))
            elif (one_current_vis):
                self._append_recInfo(enhance(self))
                self._append_recInfo(filter(self))
                self._append_recInfo(generalize(self))
            elif (multiple_current_vis):
                self._append_recInfo(custom(self))
            
        # Store _rec_info into a more user-friendly dictionary form
        self.recommendation = {}
        for rec_info in self._rec_info: 
            action_type = rec_info["action"]
            vc = rec_info["collection"]
            if (self.plot_config):
                for vis in self.current_vis: vis.plot_config = self.plot_config
                for vis in vc: vis.plot_config = self.plot_config
            if (len(vc)>0):
                self.recommendation[action_type]  = vc



    #######################################################
    ############## LuxWidget Result Display ###############
    #######################################################
    def get_widget(self):
        return self._widget

    def get_exported(self) -> typing.Union[typing.Dict[str,VisList], VisList]:
        """
        Get selected visualizations as exported Vis List

        Notes
        -----
        Convert the _exportedVisIdxs dictionary into a programmable VisList
        Example _exportedVisIdxs : 
            {'Correlation': [0, 2], 'Occurrence': [1]}
        indicating the 0th and 2nd vis from the `Correlation` tab is selected, and the 1st vis from the `Occurrence` tab is selected.
        
        Returns
        -------
        typing.Union[typing.Dict[str,VisList], VisList]
            When there are no exported vis, return empty list -> []
            When all the exported vis is from the same tab, return a VisList of selected visualizations. -> VisList(v1, v2...)
            When the exported vis is from the different tabs, return a dictionary with the action name as key and selected visualizations in the VisList. -> {"Enhance": VisList(v1, v2...), "Filter": VisList(v5, v7...), ..}
        """
        if not hasattr(self,"widget"):
            warnings.warn(
						"\nNo widget attached to the dataframe."
						"Please assign dataframe to an output variable.\n"
						"See more: https://lux-api.readthedocs.io/en/latest/source/guide/FAQ.html#troubleshooting-tips"
						, stacklevel=2)
            return []
        exported_vis_lst =self._widget._exportedVisIdxs
        exported_vis = [] 
        if (exported_vis_lst=={}):
            warnings.warn(
				"\nNo visualization selected to export.\n"
				"See more: https://lux-api.readthedocs.io/en/latest/source/guide/FAQ.html#troubleshooting-tips"
				,stacklevel=2)
            return []
        if len(exported_vis_lst) == 1 and "currentVis" in exported_vis_lst:
            return self.current_vis
        elif len(exported_vis_lst) > 1: 
            exported_vis  = {}
            if ("currentVis" in exported_vis_lst):
                exported_vis["Current Vis"] = self.current_vis
            for export_action in exported_vis_lst:
                if (export_action != "currentVis"):
                    exported_vis[export_action] = VisList(list(map(self.recommendation[export_action].__getitem__, exported_vis_lst[export_action])))
            return exported_vis
        elif len(exported_vis_lst) == 1 and ("currentVis" not in exported_vis_lst): 
            export_action = list(exported_vis_lst.keys())[0]
            exported_vis = VisList(list(map(self.recommendation[export_action].__getitem__, exported_vis_lst[export_action])))
            return exported_vis
        else:
            warnings.warn(
				"\nNo visualization selected to export.\n"
				"See more: https://lux-api.readthedocs.io/en/latest/source/guide/FAQ.html#troubleshooting-tips"
				,stacklevel=2)
            return []

    def _repr_html_(self):
        from IPython.display import display
        from IPython.display import clear_output
        import ipywidgets as widgets
        
        try: 
            if(self.index.nlevels>=2):
                warnings.warn(
                                "\nLux does not currently support dataframes "
                                "with hierarchical indexes.\n"
                                "Please convert the dataframe into a flat "
                                "table via `pandas.DataFrame.reset_index`.\n",
                                stacklevel=2,
                            )
                display(self.display_pandas())
                return

            if (len(self)<=0):
                warnings.warn("\nLux can not operate on an empty dataframe.\nPlease check your input again.\n",stacklevel=2)
                display(self.display_pandas()) 
                return

            self.toggle_pandas_display = self.default_pandas_display # Reset to Pandas Vis everytime
            # Ensure that metadata is recomputed before plotting recs (since dataframe operations do not always go through init or _refresh_intent)
            if self.executor_type == "Pandas":
                self.compute_stats()
                self.compute_dataset_metadata()

            #for benchmarking
            if self.toggle_benchmarking == True:
                tic = time.perf_counter()
            self.show_more() # compute the recommendations (TODO: This can be rendered in another thread in the background to populate self._widget)
            if self.toggle_benchmarking == True:
                toc = time.perf_counter()
                print(f"Computed recommendations in {toc - tic:0.4f} seconds")

            self._widget = LuxDataFrame.render_widget(self)

            # box = widgets.Box(layout=widgets.Layout(display='inline'))
            button = widgets.Button(description="Toggle Pandas/Lux",layout=widgets.Layout(width='140px',top='5px'))
            output = widgets.Output()
            # box.children = [button,output]
            # output.children = [button]
            # display(box)
            display(button,output)
            def on_button_clicked(b):
                with output:
                    if (b):
                        self.toggle_pandas_display = not self.toggle_pandas_display
                    clear_output()
                    if (self.toggle_pandas_display):
                        display(self.display_pandas())
                    else:
                        # b.layout.display = "none"
                        display(self._widget)
                        # b.layout.display = "inline-block"
            button.on_click(on_button_clicked)
            on_button_clicked(None)
        except(KeyboardInterrupt,SystemExit):
            raise
        # except:
        #     warnings.warn(
        #             "\nUnexpected error in rendering Lux widget and recommendations. "
        #             "Falling back to Pandas display.\n\n" 
        #             "Please report this issue on Github: https://github.com/lux-org/lux/issues "
        #         ,stacklevel=2)
        #     display(self.display_pandas())
    def display_pandas(self):
        return self.to_pandas()
    @staticmethod
    def render_widget(ldf="", renderer:str ="altair", input_current_view=""):
        """
        Generate a LuxWidget based on the LuxDataFrame
        
        Parameters
        ----------
        renderer : str, optional
            Choice of visualization rendering library, by default "altair"
        input_current_view : lux.LuxDataFrame, optional
            User-specified current vis to override default Current Vis, by default 
        """       
        check_import_lux_widget()
        import luxWidget
        widgetJSON = ldf.to_JSON(input_current_view=input_current_view)
        return luxWidget.LuxWidget(
            currentVis=widgetJSON["current_vis"],
            recommendations=widgetJSON["recommendation"],
            intent=LuxDataFrame.intent_to_string(ldf._intent)
        )
    @staticmethod
    def intent_to_JSON(intent):
        from lux.utils import utils

        filter_specs = utils.get_filter_specs(intent)
        attrs_specs = utils.get_attrs_specs(intent)
        
        intent = {}
        intent['attributes'] = [clause.attribute for clause in attrs_specs]
        intent['filters'] = [clause.attribute for clause in filter_specs]
        return intent
    @staticmethod
    def intent_to_string(intent):
        if (intent):
            return ", ".join([clause.to_string() for clause in intent])
        else:
            return ""

    def to_JSON(self, input_current_view=""):
        widget_spec = {}
        if (self.current_vis): 
            self.executor.execute(self.current_vis, self)
            widget_spec["current_vis"] = LuxDataFrame.current_view_to_JSON(self.current_vis, input_current_view)
        else:
            widget_spec["current_vis"] = {}
        widget_spec["recommendation"] = []
        
        # Recommended Collection
        recCollection = LuxDataFrame.rec_to_JSON(self._rec_info)
        widget_spec["recommendation"].extend(recCollection)
        return widget_spec
    
    @staticmethod
    def current_view_to_JSON(vc, input_current_view=""):
        current_view_spec = {}
        numVC = len(vc) #number of visualizations in the vis list
        if (numVC==1):
            current_view_spec = vc[0].render_VSpec()
        elif (numVC>1):
            pass
        return current_view_spec
    @staticmethod
    def rec_to_JSON(recs):
        rec_lst = []
        import copy
        rec_copy = copy.deepcopy(recs)
        for idx,rec in enumerate(rec_copy):
            if (len(rec["collection"])>0):
                rec["vspec"] = []
                for vis in rec["collection"]:
                    chart = vis.render_VSpec()
                    rec["vspec"].append(chart)
                rec_lst.append(rec)
                # delete DataObjectCollection since not JSON serializable
                del rec_lst[idx]["collection"]
        return rec_lst
