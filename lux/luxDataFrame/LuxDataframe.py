import pandas as pd
import lux
from lux.compiler.Validator import Validator
from lux.compiler.Compiler import Compiler
from lux.compiler.Parser import Parser
from lux.executor.ExecutionEngine import ExecutionEngine
class LuxDataFrame(pd.DataFrame):
    # MUST register here for new properties!!
    _metadata = ['context','spec','schema','attrList','dataTypeLookup','dataType', 
                 'dataModelLookup','dataModel','uniqueValues','cardinality',
                 'viewCollection','cols','rows','widget', 'recommendation']

    def __init__(self,*args, **kw):
        self.context = []
        self.spec = []
        self.schema = []
        self.recommendation=[]
        self.viewCollection = []
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
        viewCollection = Compiler.compile(self,self.viewCollection)
        self.setViewCollection(viewCollection)
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
                    self.dataTypeLookup[attr] = "nominal"
                else:
                    self.dataTypeLookup[attr] = "quantitative"
            elif self.dtypes[attr] == "object":
                self.dataTypeLookup[attr] = "nominal"
            elif pd.api.types.is_datetime64_any_dtype(self.dtypes[attr]): #check if attribute is any type of datetime dtype
                self.dataTypeLookup[attr] = "temporal"
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
            "dimension": self.dataType["ordinal"] + self.dataType["nominal"] + self.dataType["temporal"]
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
    def showMore(self):
        # TODO (Jaywoo): add back old logic after all actions are implemented
        # Old logic: 
        # currentViewExist = self.compiled.spec!=[]
        # result = lux.Result()
        # if (currentViewExist):
        #     result.mergeResult(self.enhance())
        #     result.mergeResult(self.filter())
        #     result.mergeResult(self.generalize())
        # else: 
        #     result.mergeResult(self.overview())
        
        #instead of results now, what recommendation is simply a list of ViewCollection

        # self.recommendation.append(self.correlation())
        self.setContext([lux.Spec("?",dataModel="measure")]) # Jaywoo
        self.recommendation.append(self.distribution())
        # self.recommendation.append(self.enhance())

    #######################################################
    ############## LuxWidget Result Display ###############
    #######################################################
    def getWidget(self):
        return self.widget
    def _repr_html_(self):
        from IPython.display import display
        self.renderWidget()
        display(self.widget)

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
        self.widget = luxWidget.LuxWidget(
            currentView=widgetJSON["currentView"],
            recommendations=widgetJSON["recommendation"]
        )

    def toJSON(self, inputCurrentView=""):
        widgetSpec = {}
        from lux.executor.ExecutionEngine import ExecutionEngine
        ExecutionEngine.execute(self.viewCollection,self)
        widgetSpec["currentView"] = LuxDataFrame.currentViewToJSON(self.viewCollection,inputCurrentView)
        
        widgetSpec["recommendation"] = []
        if (len(self.viewCollection)>1):
            widgetSpec["recommendation"] = [
                {"action": "Vis Collection",
                "description": "The collection of visualizations generated by the specified context.", 
                "collection": self.viewCollection
            }]
        
        # Recommended Collection
        recCollection = LuxDataFrame.recToJSON(self.recommendation)
        widgetSpec["recommendation"].extend(recCollection)
        return widgetSpec
    
    @staticmethod
    def currentViewToJSON(vc:lux.view.ViewCollection, inputCurrentView=""):
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
    def recToJSON(recs:lux.view.ViewCollection):
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


