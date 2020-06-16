import pandas as pd
from lux.context.Spec import Spec
from lux.view.View import View
from lux.view.ViewCollection import ViewCollection
from lux.utils.utils import checkImportLuxWidget
#import for benchmarking
import time
import typing
class LuxDataFrame(pd.DataFrame):
    '''
    A subclass of pd.DataFrame that supports all dataframe operations while housing other variables and functions for generating visual recommendations.
    '''
    # MUST register here for new properties!!
    _metadata = ['context','dataTypeLookup','dataType','filterSpecs',
                 'dataModelLookup','dataModel','uniqueValues','cardinality',
                 'xMinMax', 'yMinMax','plotConfig',
                 'viewCollection','widget', '_recInfo', 'recommendation']

    def __init__(self,*args, **kw):
        from lux.executor.PandasExecutor import PandasExecutor
        self.context = []
        self._recInfo=[]
        self.recommendation = {}
        self.viewCollection = []
        super(LuxDataFrame, self).__init__(*args, **kw)

        tic = time.perf_counter()
        self.computeStats()
        self.computeDatasetMetadata()

        self.executorType = "Pandas"
        self.executor = PandasExecutor
        self.SQLconnection = ""
        self.table_name = ""
        self.filterSpecs = []
        self.togglePandasView = True
        self.toggleBenchmarking = False
        self.plotConfig = None

    @property
    def _constructor(self):
        return LuxDataFrame
    
    # @property
    # def context(self):
    #     return self.context
    
    def setExecutorType(self, exe):
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
        self.executorType = exe
    def setPlotConfig(self,configFunc:typing.Callable):
        """
        Modify plot aesthetic settings to all Views in the dataframe display
        Currently only supported for Altair visualizations

        Parameters
        ----------
        configFunc : typing.Callable
            A function that takes in an AltairChart (https://altair-viz.github.io/user_guide/generated/toplevel/altair.Chart.html) as input and returns an AltairChart as output
        
        Example
        ----------
        Changing the color of marks and adding a title for all charts displayed for this dataframe

        >>> df = pd.read_csv("lux/data/car.csv")
        >>> def changeColorAddTitle(chart):
                chart = chart.configure_mark(color="red") # change mark color to red
                chart.title = "Custom Title" # add title to chart
                return chart
        >>> df.setPlotConfig(changeColorAddTitle)
        >>> df

        Change the opacity of all scatterplots displayed for this dataframe
        >>> df = pd.read_csv("lux/data/olympic.csv")
        >>> def changeOpacityScatterOnly(chart):
                if chart.mark=='circle':
                    chart = chart.configure_mark(opacity=0.1) # lower opacity
                return chart
        >>> df.setPlotConfig(changeOpacityScatterOnly)
        >>> df
        """        
        self.plotConfig = configFunc
    def clearPlotConfig(self):
        self.plotConfig = None
    def setViewCollection(self,viewCollection):
        self.viewCollection = viewCollection 
    def _refreshContext(self):
        from lux.compiler.Validator import Validator
        from lux.compiler.Compiler import Compiler
        from lux.compiler.Parser import Parser

        if self.SQLconnection == "":
            self.computeStats()
            self.computeDatasetMetadata()
        self.context = Parser.parse(self.getContext())
        Validator.validateSpec(self.context,self)
        viewCollection = Compiler.compile(self,self.context,self.viewCollection)
        self.setViewCollection(viewCollection)

    def setContext(self,context:typing.List[typing.Union[str,Spec]]):
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
        self._refreshContext()
    def setContextAsView(self,view:View):
        """
        Set context of the dataframe as the View

        Parameters
        ----------
        view : View
            [description]
        """        
        self.context = view.specLst
        self._refreshContext()

    def clearContext(self):
        self.context = []
        self.viewCollection = []
    def clearFilter(self):
        self.filterSpecs = []  # reset filters
    def toPandas(self):
        import lux.luxDataFrame
        return lux.luxDataFrame.originalDF(self,copy=False)
    def addToContext(self,context): 
        self.context.extend(context)
    def getContext(self):
        return self.context
    def __repr__(self):
        # TODO: _repr_ gets called from _repr_html, need to get rid of this call
        return ""

    #######################################################
    ############ Metadata: data type, model #############
    #######################################################
    def computeDatasetMetadata(self):
        self.dataTypeLookup = {}
        self.dataType = {}
        self.computeDataType()
        self.dataModelLookup = {}
        self.dataModel = {}
        self.computeDataModel()

    def computeDataType(self):
        for attr in list(self.columns):
            #TODO: Think about dropping NaN values
            if str(attr).lower() in ["month", "year"]:
                self.dataTypeLookup[attr] = "temporal"
            elif self.dtypes[attr] == "float64":
                self.dataTypeLookup[attr] = "quantitative"
            elif self.dtypes[attr] == "int64":
                if self.cardinality[attr] < 13: #TODO:nominal with high value breaks system
                    self.dataTypeLookup[attr] = "nominal"
                else:
                    self.dataTypeLookup[attr] = "quantitative"
            # Eliminate this clause because a single NaN value can cause the dtype to be object
            elif self.dtypes[attr] == "object":
                self.dataTypeLookup[attr] = "nominal"
            
            # TODO: quick check if attribute is of type time (auto-detect logic borrow from Zenvisage data import)
            elif pd.api.types.is_datetime64_any_dtype(self.dtypes[attr]): #check if attribute is any type of datetime dtype
                self.dataTypeLookup[attr] = "temporal"
        # for attr in list(df.dtypes[df.dtypes=="int64"].keys()):
        # 	if self.cardinality[attr]>50:
        self.dataType = self.mapping(self.dataTypeLookup)


    def computeDataModel(self):
        self.dataModel = {
            "measure": self.dataType["quantitative"],
            "dimension": self.dataType["ordinal"] + self.dataType["nominal"] + self.dataType["temporal"]
        }
        self.dataModelLookup = self.reverseMapping(self.dataModel)


    def mapping(self, rmap):
        groupMap = {}
        for val in ["quantitative", "ordinal", "nominal", "temporal"]:
            groupMap[val] = list(filter(lambda x: rmap[x] == val, rmap))
        return groupMap


    def reverseMapping(self, map):
        reverseMap = {}
        for valKey in map:
            for val in map[valKey]:
                reverseMap[val] = valKey
        return reverseMap

    def computeStats(self):
        # precompute statistics
        self.uniqueValues = {}
        self.xMinMax = {}
        self.yMinMax = {}
        self.cardinality = {}

        for attribute in self.columns:
            self.uniqueValues[attribute] = list(self[attribute].unique())
            self.cardinality[attribute] = len(self.uniqueValues[attribute])
            if self.dtypes[attribute] == "float64" or self.dtypes[attribute] == "int64":
                self.xMinMax[attribute] = (min(self.uniqueValues[attribute]), max(self.uniqueValues[attribute]))
                self.yMinMax[attribute] = (min(self.uniqueValues[attribute]), max(self.uniqueValues[attribute]))

    #######################################################
    ########## SQL Metadata, type, model schema ###########
    #######################################################

    def setSQLConnection(self, connection, t_name):
        #for benchmarking
        if self.toggleBenchmarking == True:
            tic = time.perf_counter()
        self.SQLconnection = connection
        self.table_name = t_name
        self.computeSQLDatasetMetadata()
        if self.toggleBenchmarking == True:
            toc = time.perf_counter()
            print(f"Extracted Metadata from SQL Database in {toc - tic:0.4f} seconds")
        self.setExecutorType("SQL")

    def computeSQLDatasetMetadata(self):
        self.getSQLAttributes()
        for attr in list(self.columns):
            self[attr] = None
        self.dataTypeLookup = {}
        self.dataType = {}
        #####NOTE: since we aren't expecting users to do much data processing with the SQL database, should we just keep this 
        #####      in the initialization and do it just once
        self.computeSQLDataType()
        self.computeSQLStats()
        self.dataModelLookup = {}
        self.dataModel = {}
        self.computeDataModel()

    def computeSQLStats(self):
        # precompute statistics
        self.uniqueValues = {}
        self.xMinMax = {}
        self.yMinMax = {}

        self.getSQLUniqueValues()
        #self.getSQLCardinality()
        for attribute in self.columns:
            if self.dataTypeLookup[attribute] == 'quantitative':
                self.xMinMax[attribute] = (min(self.uniqueValues[attribute]), max(self.uniqueValues[attribute]))
                self.yMinMax[attribute] = (min(self.uniqueValues[attribute]), max(self.uniqueValues[attribute]))

    def getSQLAttributes(self):
        if "." in self.table_name:
            table_name = self.table_name[self.table_name.index(".")+1:]
        else:
            table_name = self.table_name
        attr_query = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = '{}'".format(table_name)
        attributes = list(pd.read_sql(attr_query, self.SQLconnection)['column_name'])
        for attr in attributes:
            self[attr] = None

    def getSQLCardinality(self):
        cardinality = {}
        for attr in list(self.columns):
            card_query = pd.read_sql("SELECT Count(Distinct({})) FROM {}".format(attr, self.table_name), self.SQLconnection)
            cardinality[attr] = list(card_query["count"])[0]
        self.cardinality = cardinality

    def getSQLUniqueValues(self):
        uniqueVals = {}
        for attr in list(self.columns):
            unique_query = pd.read_sql("SELECT Distinct({}) FROM {}".format(attr, self.table_name), self.SQLconnection)
            uniqueVals[attr] = list(unique_query[attr])
        self.uniqueValues = uniqueVals

    def computeSQLDataType(self):
        dataTypeLookup = {}
        sqlDTypes = {}
        self.getSQLCardinality()
        if "." in self.table_name:
            table_name = self.table_name[self.table_name.index(".")+1:]
        else:
            table_name = self.table_name
        #get the data types of the attributes in the SQL table
        for attr in list(self.columns):
            datatype_query = "SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}' AND COLUMN_NAME = '{}'".format(table_name, attr)
            datatype = list(pd.read_sql(datatype_query, self.SQLconnection)['data_type'])[0]
            sqlDTypes[attr] = datatype

        dataType = {"quantitative":[], "ordinal":[], "nominal":[], "temporal":[]}
        for attr in list(self.columns):
            if str(attr).lower() in ["month", "year"]:
                dataTypeLookup[attr] = "temporal"
                dataType["temporal"].append(attr)
            elif sqlDTypes[attr] in ["character", "character varying", "boolean", "uuid", "text"]:
                dataTypeLookup[attr] = "nominal"
                dataType["nominal"].append(attr)
            elif sqlDTypes[attr] in ["integer", "real", "smallint", "smallserial", "serial"]:
                if self.cardinality[attr] < 13:
                    dataTypeLookup[attr] = "nominal"
                    dataType["nominal"].append(attr)
                else:
                    dataTypeLookup[attr] = "quantitative"
                    dataType["quantitative"].append(attr)
            elif "time" in sqlDTypes[attr] or "date" in sqlDTypes[attr]:
                dataTypeLookup[attr] = "temporal"
                dataType["temporal"].append(attr)
        self.dataTypeLookup = dataTypeLookup
        self.dataType = dataType

    def showMore(self):
        from lux.action.UserDefined import userDefined
        from lux.action.Correlation import correlation
        from lux.action.Distribution import distribution
        from lux.action.Enhance import enhance
        from lux.action.Filter import filter
        from lux.action.Generalize import generalize

        self._recInfo = []
        noView = len(self.viewCollection) == 0
        oneCurrentView = len(self.viewCollection) == 1
        multipleCurrentViews = len(self.viewCollection) > 1

        if (noView):
            self._recInfo.append(correlation(self))
            self._recInfo.append(distribution(self,"quantitative"))
            self._recInfo.append(distribution(self,"nominal"))
        elif (oneCurrentView):
            enhance = enhance(self)
            filter = filter(self)
            generalize = generalize(self)
            if enhance['collection']:
                self._recInfo.append(enhance)
            if filter['collection']:
                self._recInfo.append(filter)
            if generalize['collection']:
                self._recInfo.append(generalize)
        elif (multipleCurrentViews):
            self._recInfo.append(userDefined(self))
            
        # Store _recInfo into a more user-friendly dictionary form
        self.recommendation = {}
        for recInfo in self._recInfo: 
            actionType = recInfo["action"]
            vc = recInfo["collection"]
            if (self.plotConfig):
                for view in vc: view.plotConfig = self.plotConfig
            self.recommendation[actionType]  = vc

        self.clearFilter()



    #######################################################
    ############## LuxWidget Result Display ###############
    #######################################################
    def getWidget(self):
        return self.widget

    def getExported(self) -> typing.Union[typing.Dict[str,ViewCollection], ViewCollection]:
        """
        Convert the _exportedVisIdxs dictionary into a programmable ViewCollection
        Example _exportedVisIdxs : 
            {'Correlation': [0, 2], 'Category': [1]}
        indicating the 0th and 2nd vis from the `Correlation` tab is selected, and the 1st vis from the `Category` tab is selected.
        
        Returns
        -------
        typing.Union[typing.Dict[str,ViewCollection], ViewCollection]
            When there are no exported vis, return empty list -> []
            When all the exported vis is from the same tab, return a ViewCollection of selected views. -> ViewCollection(v1, v2...)
            When the exported vis is from the different tabs, return a dictionary with the action name as key and selected views in the ViewCollection. -> {"Enhance": ViewCollection(v1, v2...), "Filter": ViewCollection(v5, v7...), ..}
        """        
        exportedVisLst =self.widget._exportedVisIdxs
        exportedViews = [] 
        if len(exportedVisLst) == 1 : 
            exportAction = list(exportedVisLst.keys())[0]
            exportedViews = ViewCollection(list(map(self.recommendation[exportAction].__getitem__, exportedVisLst[exportAction])))
        elif len(exportedVisLst) > 1 : 
            exportedViews  = {}
            for exportAction in exportedVisLst: 
                exportedViews[exportAction] = ViewCollection(list(map(self.recommendation[exportAction].__getitem__, exportedVisLst[exportAction])))
        return exportedViews

    def _repr_html_(self):
        from IPython.display import display
        from IPython.display import clear_output
        import ipywidgets as widgets
        # Ensure that metadata is recomputed before plotting recs (since dataframe operations do not always go through init or _refreshContext)
        if self.executorType == "Pandas":
            self.computeStats()
            self.computeDatasetMetadata()
        #for benchmarking
        if self.toggleBenchmarking == True:
            tic = time.perf_counter()
        self.showMore() # compute the recommendations
        if self.toggleBenchmarking == True:
            toc = time.perf_counter()
            print(f"Computed recommendations in {toc - tic:0.4f} seconds")

        self.widget = LuxDataFrame.renderWidget(self)

        button = widgets.Button(description="Toggle Pandas/Lux")
        output = widgets.Output()

        display(button, output)

        def on_button_clicked(b):
            with output:
                if (b):
                    self.togglePandasView = not self.togglePandasView
                clear_output()
                if (self.togglePandasView):
                    display(self.displayPandas())
                else:
                    display(self.widget)

        button.on_click(on_button_clicked)
        on_button_clicked(None)

    def displayPandas(self):
        return self.toPandas()
    @staticmethod
    def renderWidget(ldf="", renderer:str ="altair", inputCurrentView=""):
        """
        Generate a LuxWidget based on the LuxDataFrame
        
        Parameters
        ----------
        renderer : str, optional
            Choice of visualization rendering library, by default "altair"
        inputCurrentView : lux.LuxDataFrame, optional
            User-specified current view to override default Current View, by default 
        """       
        checkImportLuxWidget()
        import luxWidget
        widgetJSON = ldf.toJSON(inputCurrentView=inputCurrentView)
        return luxWidget.LuxWidget(
            currentView=widgetJSON["currentView"],
            recommendations=widgetJSON["recommendation"],
            context=LuxDataFrame.contextToJSON(ldf.context)
        )
    @staticmethod
    def contextToJSON(context):
        from lux.utils import utils

        filterSpecs = utils.getFilterSpecs(context)
        attrsSpecs = utils.getAttrsSpecs(context)
        
        specs = {}
        specs['attributes'] = [spec.attribute for spec in attrsSpecs]
        specs['filters'] = [spec.attribute for spec in filterSpecs]
        return specs

    def toJSON(self, inputCurrentView=""):
        widgetSpec = {}
        self.executor.execute(self.viewCollection,self)
        widgetSpec["currentView"] = LuxDataFrame.currentViewToJSON(self.viewCollection,inputCurrentView)
        
        widgetSpec["recommendation"] = []
        
        # Recommended Collection
        recCollection = LuxDataFrame.recToJSON(self._recInfo)
        widgetSpec["recommendation"].extend(recCollection)
        return widgetSpec
    
    @staticmethod
    def currentViewToJSON(vc, inputCurrentView=""):
        currentViewSpec = {}
        numVC = len(vc) #number of views in the view collection
        if (numVC==1):
            currentViewSpec = vc[0].renderVSpec()
        elif (numVC>1):
            pass
        return currentViewSpec
    @staticmethod
    def recToJSON(recs):
        recLst = []
        import copy
        recCopy = copy.deepcopy(recs)
        for idx,rec in enumerate(recCopy):
            if (rec != {}):
                rec["vspec"] = []
                for vis in rec["collection"]:
                    chart = vis.renderVSpec()
                    rec["vspec"].append(chart)
                recLst.append(rec)
                # delete DataObjectCollection since not JSON serializable
                del recLst[idx]["collection"]
        return recLst


