import pandas as pd
import lux
from lux.compiler.Validator import Validator
from lux.compiler.Compiler import Compiler
from lux.compiler.Parser import Parser
from lux.executor.ExecutionEngine import ExecutionEngine
import luxWidget
class LuxDataFrame(pd.DataFrame):
    # MUST register here for new properties!!
    _metadata = ['context','spec','schema','attrList','dataTypeLookup','dataType', 
                 'dataModelLookup','dataModel','uniqueValues','cardinality','viewCollection','cols','rows','widget']

    def __init__(self,*args, **kw):
        self.context = []
        self.spec = []
        self.viewCollection = ""
        self.schema = []
        super(LuxDataFrame, self).__init__(*args, **kw)
        self.computeStats()
        self.computeDatasetMetadata()

    @property
    def _constructor(self):
        return LuxDataFrame
    def setViewCollection(self,viewCollection):
        self.viewCollection = viewCollection 
    def _refreshContext(self,context):
        self.computeStats()
        self.computeDatasetMetadata()
        Parser.parse(self)
        Validator.validateSpec(self)
        Compiler.compile(self)
    def setContext(self,context):
        self.context = context
        self._refreshContext(context)
    def addToContext(self,context): 
        self.context.extend(context)
    def getContext(self):
        return self.context
    def __repr__(self):
        # TODO: _repr_ gets called from _repr_html, need to get rid of this call
        return ""

    #######################################################
    ############ Metadata, type, model schema #############
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
            if self.dtypes[attr] == "float64" or self.dtypes[attr] == "int64":
                if self.cardinality[attr] < 10:
                    self.dataTypeLookup[attr] = "categorical"
                else:
                    self.dataTypeLookup[attr] = "quantitative"
            elif self.dtypes[attr] == "object":
                self.dataTypeLookup[attr] = "categorical"
            elif pd.api.types.is_datetime64_any_dtype(self.dtypes[attr]): #check if attribute is any type of datetime dtype
                self.dataTypeLookup[attr] = "date"
        # # Override with schema specified types
        for attrInfo in self.schema:
            key = list(attrInfo.keys())[0]
            if ("dataType" in attrInfo[key]):
                self.dataTypeLookup[key] = attrInfo[key]["dataType"]
        # for attr in list(df.dtypes[df.dtypes=="int64"].keys()):
        # 	if self.cardinality[attr]>50:
        self.dataType = self.mapping(self.dataTypeLookup)


    def computeDataModel(self):
        # TODO: Need to be modified to take in schema for overriding defaults
        self.dataModel = {
            "measure": self.dataType["quantitative"],
            "dimension": self.dataType["ordinal"] + self.dataType["categorical"] + self.dataType["date"]
        }
        # Override with schema specified types
        for attrInfo in self.schema:
            key = list(attrInfo.keys())[0]
            if ("dataModel" in attrInfo[key]):
                dataModel = attrInfo[key]["dataModel"]
                if (dataModel == "measure"):
                    self.dataModel["dimension"].remove(key)
                    self.dataModel["measure"].append(key)
                else:
                    self.dataModel["measure"].remove(key)
                    self.dataModel["dimension"].append(key)
        self.dataModelLookup = self.reverseMapping(self.dataModel)


    def mapping(self, rmap):
        groupMap = {}
        for val in ["quantitative", "ordinal", "categorical", "date"]:
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
    ############## Mappers to Action classes ##############
    #######################################################
    def correlation(self):
        from lux.action.Correlation import correlation
        return correlation(self)

    # def showMore(self):
    #     currentViewExist = self.compiled.spec!=[]
    #     ExecutionEngine.execute(self)  # data is available for each view in the spec.
    #     result = lux.Result()
    #     result.mergeResult(self.overview())
    #     return result

    #######################################################
    ############## LuxWidget Result Display ###############
    #######################################################
    def getWidget(self):
        return self.widget
    def _repr_html_(self):
        from IPython.display import display
        widget = self.renderWidget()
        display(widget)

    def renderWidget(self, renderer:str ="altair", inputCurrentView="") -> luxWidget.LuxWidget:
        """
        Generate a LuxWidget based on the LuxDataFrame
        
        Parameters
        ----------
        renderer : str, optional
            Choice of visualization rendering library, by default "altair"
        inputCurrentView : lux.LuxDataFrame, optional
            User-specified current view to override defaul Current View, by default ""
        
        Returns
        -------
        luxWidget.LuxWidget
            Returned widget (also stored as self.widget)
        """        
        import pkgutil
        if (pkgutil.find_loader("luxWidget") is None):
            raise Exception("luxWidget is not install. Run `npm i lux-widget' to install the Jupyter widget.\nSee more at: https://github.com/lux-org/lux-widget")
        # widgetJSON = self.toJSON(inputCurrentView=inputCurrentView)
        # For debugging purposes
        import json
        widgetJSON = json.load(open("mockWidgetJSON.json",'r'))
        self.widget = luxWidget.LuxWidget(
            currentView=widgetJSON["currentView"],
            recommendations=widgetJSON["recommendations"]
        )
        return self.widget

    def toJSON(self, inputCurrentView=""):
        dobj_dict = {}
        from lux.executor.ExecutionEngine import ExecutionEngine
        ExecutionEngine.execute(self.viewCollection,self)
        dobj_dict["currentView"] = LuxDataFrame.currentViewToJSON(self.viewCollection,inputCurrentView)
        # if (dobj.recommendations==[]):
        #     visCollection = {"action": "Vis Collection",
        #         "collection":dobj.compiled
        #     }
        #     dobj.recommendations.append(visCollection)
        # # Recommended Collection
        # dobj_dict["recommendations"] = LuxDataFrame.recToJSON(self.resultsJSON)
        return dobj_dict
    
    @staticmethod
    def currentViewToJSON(vc, inputCurrentView=""):
        currentViewSpec = {}
        numVC = len(vc) #number of views in the view collection
        if (numVC==1):
            currentViewSpec = vc[0].renderVSpec()
        elif (numVC>1):
            pass
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
    # @staticmethod
    # def recToJSON(recDataObjs):
    #     recLst = []
    #     import copy
    #     recCopy = copy.deepcopy(recDataObjs)
    #     # for the case of single DataObject display of vis collection 
    #     if (type(recCopy)!=list): recCopy = [recCopy]
    #     for idx,rec in enumerate(recCopy):
    #         if (rec != {}):
    #             rec["vspec"] = []
    #             for vis in rec["collection"].collection:
    #                 chart = vis.renderVSpec()
    #                 rec["vspec"].append(chart)
    #             recLst.append(rec)
    #             # delete DataObjectCollection since not JSON serializable
    #             del recLst[idx]["collection"]
    #     return recLst


