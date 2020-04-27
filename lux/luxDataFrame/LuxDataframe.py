import pandas as pd
import psycopg2
from lux.context.Spec import Spec
class LuxDataFrame(pd.DataFrame):
    # MUST register here for new properties!!
    _metadata = ['context','attrList','dataTypeLookup','dataType', 
                 'dataModelLookup','dataModel','uniqueValues','cardinality',
                 'viewCollection','cols','rows','widget', 'recommendation']

    def __init__(self,*args, **kw):
        self.context = []
        self.recommendation=[]
        self.viewCollection = []
        super(LuxDataFrame, self).__init__(*args, **kw)
        self.computeStats()
        self.computeDatasetMetadata()
        self.DEBUG_FRONTEND = False

        self.SQLconnection = ""
        self.table_name = ""

    @property
    def _constructor(self):
        return LuxDataFrame
    
    # @property
    # def context(self):
    #     return self.context
    
    
    def setViewCollection(self,viewCollection):
        self.viewCollection = viewCollection 
    def _refreshContext(self,context):
        from lux.compiler.Validator import Validator
        from lux.compiler.Compiler import Compiler
        from lux.compiler.Parser import Parser
        from lux.executor.PandasExecutor import PandasExecutor
        if self.SQLconnection == "":
            self.computeStats()
            self.computeDatasetMetadata()
        else:
            self.computeSQLStats()
            self.computeSQLDatasetMetadata()
        Parser.parse(self)
        Validator.validateSpec(self)
        viewCollection = Compiler.compile(self,self.viewCollection)
        self.setViewCollection(viewCollection)
    def setContext(self,context):
        self.context = context
        self._refreshContext(context)
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
        self.attrList = list(self.columns)
        self.cols = []
        self.rows = []
        self.dataTypeLookup = {}
        self.dataType = {}
        self.computeDataType()
        self.dataModelLookup = {}
        self.dataModel = {}
        self.computeDataModel()

    def computeDataType(self):
        for attr in self.attrList:
            #TODO: Think about dropping NaN values
            if self.dtypes[attr] == "float64" or self.dtypes[attr] == "int64":
                if self.cardinality[attr] < 10: #TODO:nominal with high value breaks system
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
        self.cardinality = {}

        for dimension in self.columns:
            self.uniqueValues[dimension] = self[dimension].unique()
            self.cardinality[dimension] = len(self.uniqueValues[dimension])

    #######################################################
    ########## SQL Metadata, type, model schema ###########
    #######################################################

    def setSQLConnection(self, connection, t_name):
        self.SQLconnection = connection
        self.table_name = t_name
        self.computeSQLDatasetMetadata()

    def computeSQLDatasetMetadata(self):
        self.getSQLAttributes()
        self.computeSQLStats()
        self.cols = []
        self.rows = []
        self.dataTypeLookup = {}
        self.dataType = {}
        #####NOTE: since we aren't expecting users to do much data processing with the SQL database, should we just keep this 
        #####      in the initialization and do it just once
        self.computeSQLDataType()
        self.dataModelLookup = {}
        self.dataModel = {}
        self.computeDataModel()

    def computeSQLStats(self):
        # precompute statistics
        self.uniqueValues = {}
        self.cardinality = {}

        self.getSQLUniqueValues()
        self.getSQLCardinality()

    def getSQLAttributes(self):
        if "." in self.table_name:
            table_name = self.table_name[self.table_name.index(".")+1:]
        else:
            table_name = self.table_name
        attr_query = "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = '{}'".format(table_name)
        attributes = pd.read_sql(attr_query, self.SQLconnection)
        self.attrList = list(attributes["column_name"])

    def getSQLCardinality(self):
        cardinality = {}
        for attr in self.attrList:
            card_query = pd.read_sql("SELECT Count(Distinct({})) FROM {}".format(attr, self.table_name), self.SQLconnection)
            cardinality[attr] = list(card_query["count"])[0]
        self.cardinality = cardinality

    def getSQLUniqueValues(self):
        uniqueVals = {}
        for attr in self.attrList:
            unique_query = pd.read_sql("SELECT Distinct({}) FROM {}".format(attr, self.table_name), self.SQLconnection)
            uniqueVals[attr] = list(unique_query[attr])
        self.uniqueValues = uniqueVals

    def computeSQLDataType(self):
        dataTypeLookup = {}
        sqlDTypes = {}
        if "." in self.table_name:
            table_name = self.table_name[self.table_name.index(".")+1:]
        else:
            table_name = self.table_name
        #get the data types of the attributes in the SQL table
        for attr in self.attrList:
            datatype_query = "SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}' AND COLUMN_NAME = '{}'".format(table_name, attr)
            datatype = list(pd.read_sql(datatype_query, self.SQLconnection)['data_type'])[0]
            sqlDTypes[attr] = datatype

        dataType = {"quantitative":[], "ordinal":[], "nominal":[], "temporal":[]}
        for attr in self.attrList:
            if sqlDTypes[attr] in ["character", "character varying", "boolean"]:
                dataTypeLookup[attr] = "nominal"
                dataType["nominal"].append(attr)
            elif sqlDTypes[attr] in ["real", "smallint", "smallserial", "serial"]:
                if self.cardinality[attr] < 10:
                    dataTypeLookup[attr] = "nominal"
                    dataType["nominal"].append(attr)
                else:
                    dataTypeLookup[attr] = "quantitative"
                    dataType["quantitative"].append(attr)
            elif "time" in sqlDTypes[attr]:
                dataTypeLookup[attr] = "temporal"
                dataType["temporal"].append(attr)
        self.dataTypeLookup = dataTypeLookup
        self.dataType = dataType

    #######################################################
    ############## Mappers to Action classes ##############
    #######################################################
    def correlation(self):
        from lux.action.Correlation import correlation
        return correlation(self)
    def distribution(self):
        from lux.action.Distribution import distribution
        return distribution(self)
    def enhance(self):
        from lux.action.Enhance import enhance
        return enhance(self)
    def filter(self):
        from lux.action.Filter import filter
        return filter(self)
    def generalize(self):
        from lux.action.Generalize import generalize
        return generalize(self)
    def similarPattern(self,query,topK=-1):
        from lux.action.Similarity import similarPattern
        self.recommendation.append(similarPattern(self,query,topK))
        self.renderWidget()
        display(self.widget)

    def showMore(self):
        self.recommendation = []
        currentViewExist = self.viewCollection!=[]
        if (self.DEBUG_FRONTEND):
            self.recommendation.append(self.generalize())
        else:
            if (currentViewExist):
                enhance = self.enhance()
                filter = self.filter()
                generalize = self.generalize()
                if enhance['collection']:
                    self.recommendation.append(enhance)
                if filter['collection']:
                    self.recommendation.append(filter)
                if generalize['collection']:
                    self.recommendation.append(generalize)
            else: 
                self.setContext([Spec("?",dataModel="measure"),Spec("?",dataModel="measure")])
                self.recommendation.append(self.correlation())  #this works partially
                self.setContext([Spec("?",dataModel="measure")])
                self.recommendation.append(self.distribution())  


    #######################################################
    ############## LuxWidget Result Display ###############
    #######################################################
    def getWidget(self):
        return self.widget
    def _repr_html_(self):
        from IPython.display import display
        self.renderWidget()
        display(self.widget)
    def displayPandas(self):
        return self.toPandas()

    def renderWidget(self, renderer:str ="altair", inputCurrentView=""):
        """
        Generate a LuxWidget based on the LuxDataFrame
        
        Parameters
        ----------
        renderer : str, optional
            Choice of visualization rendering library, by default "altair"
        inputCurrentView : lux.LuxDataFrame, optional
            User-specified current view to override defaul Current View, by default 
        """       
        import luxWidget
        self.showMore() # compute the recommendations
        import pkgutil
        if (pkgutil.find_loader("luxWidget") is None):
            raise Exception("luxWidget is not install. Run `npm i lux-widget' to install the Jupyter widget.\nSee more at: https://github.com/lux-org/lux-widget")
        widgetJSON = self.toJSON(inputCurrentView=inputCurrentView)
        # For debugging purposes
        # import json
        # widgetJSON = json.load(open("mockWidgetJSON.json",'r'))
        # print(widgetJSON["recommendation"])
        self.widget = luxWidget.LuxWidget(
            currentView=widgetJSON["currentView"],
            recommendations=widgetJSON["recommendation"],
            context=self.contextToJSON()
        )

    def contextToJSON(self):
        from lux.utils import utils

        filterSpecs = utils.getFilterSpecs(self.context)
        attrsSpecs = utils.getAttrsSpecs(self.context)
        
        specs = {}
        specs['attributes'] = [spec.attribute for spec in attrsSpecs]
        specs['filters'] = [spec.attribute for spec in filterSpecs]
        return specs

    def toJSON(self, inputCurrentView=""):
        from lux.executor.PandasExecutor import PandasExecutor
        widgetSpec = {}
        PandasExecutor.execute(self.viewCollection,self)
        widgetSpec["currentView"] = LuxDataFrame.currentViewToJSON(self.viewCollection,inputCurrentView)
        
        widgetSpec["recommendation"] = []
        # if (len(self.viewCollection)>1):
        #     widgetSpec["recommendation"] = [
        #         {"action": "Vis Collection",
        #         "description": "The collection of visualizations generated by the specified context.",
        #         "collection": self.viewCollection
        #     }
        #     ]
        
        # Recommended Collection
        recCollection = LuxDataFrame.recToJSON(self.recommendation)
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
        # This behavior is jarring to user, so comment out for now
        #     # if the compiled object is a collection, see if we can remove the elements with "?" and generate a Current View
        #     specifiedDobj = currentViewDobj.getVariableFieldsRemoved()
        #     if (specifiedDobj.spec!=[]): specifiedDobj.compile(enumerateCollection=False)
        #     if (currentView!=""):
        #         currentViewSpec = currentView.compiled.renderVSpec()
        #     elif (specifiedDobj.isEmpty()):
        #         currentViewSpec = {}
        #     else:
        #         specifiedDobj.compile(enumerateCollection=False)
        #         currentViewSpec = specifiedDobj.compiled.renderVSpec()
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


