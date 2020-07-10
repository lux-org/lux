import pandas as pd
from lux.context.Spec import Spec
from lux.view.View import View
from lux.view.ViewCollection import ViewCollection
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
    _metadata = ['context','data_type_lookup','data_type','filter_specs',
                 'data_model_lookup','data_model','unique_values','cardinality',
                 'x_min_max', 'y_min_max','plot_config',
                 'current_view','widget', '_rec_info', 'recommendation']

    def __init__(self,*args, **kw):
        from lux.executor.PandasExecutor import PandasExecutor
        self.context = []
        self._rec_info=[]
        self.recommendation = {}
        self.current_view = []
        super(LuxDataFrame, self).__init__(*args, **kw)

        self.compute_stats()
        self.compute_dataset_metadata()

        self.executor_type = "Pandas"
        self.executor = PandasExecutor
        self.SQLconnection = ""
        self.table_name = ""
        self.filter_specs = []
        self.default_pandas_view = True
        self.toggle_pandas_view = True
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
            self.default_pandas_view = False
        elif (type.lower()=="pandas"):
            self.default_pandas_view = True
        else: 
            warnings.warn("Unsupported display type. Default display option should either be `lux` or `pandas`.")
    # @property
    # def context(self):
    #     return self.context
    
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
        Modify plot aesthetic settings to all Views in the dataframe display
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
    def set_view_collection(self,view_collection):
        self.current_view = view_collection
    def _refresh_context(self):
        from lux.compiler.Validator import Validator
        from lux.compiler.Compiler import Compiler
        from lux.compiler.Parser import Parser

        if self.SQLconnection == "":
            self.compute_stats()
            self.compute_dataset_metadata()
        self.context = Parser.parse(self.get_context())
        Validator.validate_spec(self.context,self)
        view_collection = Compiler.compile(self, self.context, self.current_view)
        self.set_view_collection(view_collection)

    def set_context(self, context:typing.List[typing.Union[str, Spec]]):
        """
        Main function to set the context of the dataframe.
        The context input goes through the parser, so that the string inputs are parsed into a lux.Spec object.

        Parameters
        ----------
        context : typing.List[str,Spec]
            Context list, can be a mix of string shorthand or a lux.Spec object

        Notes
        -----
            :doc:`../guide/spec`
        """        
        self.context = context
        self._refresh_context()
    def set_context_as_view(self,view:View):
        """
        Set context of the dataframe as the View

        Parameters
        ----------
        view : View
            [description]
        """        
        self.context = view.spec_lst
        self._refresh_context()

    def clear_context(self):
        self.context = []
        self.current_view = []
    def clear_filter(self):
        self.filter_specs = []  # reset filters
    def to_pandas(self):
        import lux.luxDataFrame
        return lux.luxDataFrame.originalDF(self,copy=False)
    def add_to_context(self,context): 
        self.context.extend(context)
    def get_context(self):
        return self.context
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
                if self.cardinality[attr] < 13: #TODO:nominal with high value breaks system
                    self.data_type_lookup[attr] = "nominal"
                else:
                    self.data_type_lookup[attr] = "quantitative"
            # Eliminate this clause because a single NaN value can cause the dtype to be object
            elif self.dtypes[attr] == "object":
                self.data_type_lookup[attr] = "nominal"
            
            # TODO: quick check if attribute is of type time (auto-detect logic borrow from Zenvisage data import)
            elif pd.api.types.is_datetime64_any_dtype(self.dtypes[attr]) or pd.api.types.is_period_dtype(self.dtypes[attr]): #check if attribute is any type of datetime dtype
                self.data_type_lookup[attr] = "temporal"
        # for attr in list(df.dtypes[df.dtypes=="int64"].keys()):
        # 	if self.cardinality[attr]>50:
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
        self.x_min_max = {}
        self.y_min_max = {}
        self.cardinality = {}

        for attribute in self.columns:
            self.unique_values[attribute] = list(self[attribute].unique())
            self.cardinality[attribute] = len(self.unique_values[attribute])
            if self.dtypes[attribute] == "float64" or self.dtypes[attribute] == "int64":
                self.x_min_max[attribute] = (min(self.unique_values[attribute]), max(self.unique_values[attribute]))
                self.y_min_max[attribute] = (min(self.unique_values[attribute]), max(self.unique_values[attribute]))

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
        self.x_min_max = {}
        self.y_min_max = {}

        self.get_SQL_unique_values()
        #self.get_SQL_cardinality()
        for attribute in self.columns:
            if self.data_type_lookup[attribute] == 'quantitative':
                self.x_min_max[attribute] = (min(self.unique_values[attribute]), max(self.unique_values[attribute]))
                self.y_min_max[attribute] = (min(self.unique_values[attribute]), max(self.unique_values[attribute]))

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

    def show_more(self):
        from lux.action.UserDefined import user_defined
        from lux.action.Correlation import correlation
        from lux.action.Univariate import univariate
        from lux.action.Enhance import enhance
        from lux.action.Filter import filter
        from lux.action.Generalize import generalize

        self._rec_info = []
        no_view = len(self.current_view) == 0
        one_current_view = len(self.current_view) == 1
        multiple_current_views = len(self.current_view) > 1

        if (no_view):
            self._rec_info.append(correlation(self))
            self._rec_info.append(univariate(self,"quantitative"))
            self._rec_info.append(univariate(self,"nominal"))
            self._rec_info.append(univariate(self,"temporal"))
        elif (one_current_view):
            enhance = enhance(self)
            filter = filter(self)
            generalize = generalize(self)
            if enhance['collection']:
                self._rec_info.append(enhance)
            if filter['collection']:
                self._rec_info.append(filter)
            if generalize['collection']:
                self._rec_info.append(generalize)
        elif (multiple_current_views):
            self._rec_info.append(user_defined(self))
            
        # Store _rec_info into a more user-friendly dictionary form
        self.recommendation = {}
        for rec_info in self._rec_info: 
            action_type = rec_info["action"]
            vc = rec_info["collection"]
            if (self.plot_config):
                for view in vc: view.plot_config = self.plot_config
            if (len(vc)>0):
                self.recommendation[action_type]  = vc

        self.clear_filter()



    #######################################################
    ############## LuxWidget Result Display ###############
    #######################################################
    def get_widget(self):
        return self.widget

    def get_exported(self) -> typing.Union[typing.Dict[str,ViewCollection], ViewCollection]:
        """
        Get selected views as exported View Collection

        Notes
        -----
        Convert the _exported_vis_idxs dictionary into a programmable ViewCollection
        Example _exported_vis_idxs : 
            {'Correlation': [0, 2], 'Category': [1]}
        indicating the 0th and 2nd vis from the `Correlation` tab is selected, and the 1st vis from the `Category` tab is selected.
        
        Returns
        -------
        typing.Union[typing.Dict[str,ViewCollection], ViewCollection]
            When there are no exported vis, return empty list -> []
            When all the exported vis is from the same tab, return a ViewCollection of selected views. -> ViewCollection(v1, v2...)
            When the exported vis is from the different tabs, return a dictionary with the action name as key and selected views in the ViewCollection. -> {"Enhance": ViewCollection(v1, v2...), "Filter": ViewCollection(v5, v7...), ..}
        """        
        exported_vis_lst =self.widget._exportedVisIdxs
        exported_views = [] 
        if (exported_vis_lst=={}):
            import warnings
            warnings.warn("No visualization selected to export")
            return []
        if len(exported_vis_lst) == 1 : 
            export_action = list(exported_vis_lst.keys())[0]
            exported_views = ViewCollection(list(map(self.recommendation[export_action].__getitem__, exported_vis_lst[export_action])))
        elif len(exported_vis_lst) > 1 : 
            exported_views  = {}
            for export_action in exported_vis_lst: 
                exported_views[export_action] = ViewCollection(list(map(self.recommendation[export_action].__getitem__, exported_vis_lst[export_action])))
        return exported_views

    def _repr_html_(self):
        from IPython.display import display
        from IPython.display import clear_output
        import ipywidgets as widgets
        self.toggle_pandas_view = self.default_pandas_view # Reset to Pandas View everytime
        # Ensure that metadata is recomputed before plotting recs (since dataframe operations do not always go through init or _refresh_context)
        if self.executor_type == "Pandas":
            self.compute_stats()
            self.compute_dataset_metadata()

        #for benchmarking
        if self.toggle_benchmarking == True:
            tic = time.perf_counter()
        self.show_more() # compute the recommendations (TODO: This can be rendered in another thread in the background to populate self.widget)
        if self.toggle_benchmarking == True:
            toc = time.perf_counter()
            print(f"Computed recommendations in {toc - tic:0.4f} seconds")

        self.widget = LuxDataFrame.render_widget(self)

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
                    self.toggle_pandas_view = not self.toggle_pandas_view
                clear_output()
                if (self.toggle_pandas_view):
                    display(self.display_pandas())
                else:
                    # b.layout.display = "none"
                    display(self.widget)
                    # b.layout.display = "inline-block"
        button.on_click(on_button_clicked)
        on_button_clicked(None)

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
            User-specified current view to override default Current View, by default 
        """       
        check_import_lux_widget()
        import luxWidget
        widgetJSON = ldf.to_JSON(input_current_view=input_current_view)
        return luxWidget.LuxWidget(
            currentView=widgetJSON["current_view"],
            recommendations=widgetJSON["recommendation"],
            context=LuxDataFrame.context_to_JSON(ldf.context)
        )
    @staticmethod
    def context_to_JSON(context):
        from lux.utils import utils

        filter_specs = utils.get_filter_specs(context)
        attrs_specs = utils.get_attrs_specs(context)
        
        specs = {}
        specs['attributes'] = [spec.attribute for spec in attrs_specs]
        specs['filters'] = [spec.attribute for spec in filter_specs]
        return specs

    def to_JSON(self, input_current_view=""):
        widget_spec = {}
        self.executor.execute(self.current_view, self)
        widget_spec["current_view"] = LuxDataFrame.current_view_to_JSON(self.current_view, input_current_view)
        
        widget_spec["recommendation"] = []
        
        # Recommended Collection
        recCollection = LuxDataFrame.rec_to_JSON(self._rec_info)
        widget_spec["recommendation"].extend(recCollection)
        return widget_spec
    
    @staticmethod
    def current_view_to_JSON(vc, input_current_view=""):
        current_view_spec = {}
        numVC = len(vc) #number of views in the view collection
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


