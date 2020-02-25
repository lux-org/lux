import pandas as pd
class LuxDataFrame(pd.DataFrame):
    # normal properties
    _metadata = ['context','spec','schema','attrList','dataTypeLookup','dataType','computeDataType',
                 'dataModelLookup','dataModel','uniqueValues','cardinality'] # must register here for new properties!!

    def __init__(self,*args, schema = [], **kw):
        self.context = []
        self.spec = []
        self.schema = schema
        super(LuxDataFrame, self).__init__(*args, **kw)
        self.computeStats()
        self.computeDatasetMetadata()

    @property
    def _constructor(self):
        return LuxDataFrame

    def setContext(self,context):
        self.context = context
    def addToContext(self,context): 
        self.context.extend(context)
    def getContext(self):
        return self.context
    def __repr__(self):
        # TODO: _repr_ gets called from _repr_html, need to get rid of this call
        return ""
    def _repr_html_(self):
        import luxWidget
        import json
        widgetJSON = json.load(open("mockWidgetJSON.json",'r'))
        widget = luxWidget.LuxWidget(
            currentView=widgetJSON["currentView"],
            recommendations=widgetJSON["recommendations"]
        )
        # return widget
        from IPython.display import display
        display(widget)

    def computeDatasetMetadata(self):
        self.attrList = list(self.columns)
        self.dataTypeLookup = {}
        self.dataType = {}
        self.computeDataType()
        self.dataModelLookup = {}
        self.dataModel = {}
        self.computeDataModel()

    def computeDataType(self):
        # df = self
        # self.dataType = {
        # 	"quantitative":list(dfw.dtypes[df.dtypes=="float64"].keys()) + list(df.dtypes[df.dtypes=="int64"].keys()),
        # 	"categorical":list(df.dtypes[df.dtypes=="object"].keys()),
        # 	"ordinal": [],
        # 	"date":[]
        # }

        for attr in self.attrList:
            if self.dtypes[attr] == "float64" or self.dtypes[attr] == "int64":
                if self.cardinality[attr] < 10:
                    self.dataTypeLookup[attr] = "categorical"
                else:
                    self.dataTypeLookup[attr] = "quantitative"
            elif self.dtypes[attr] == "object":
                self.dataTypeLookup[attr] = "categorical"
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


    def mapping(self, rmap):
        groupMap = {}
        uniqueVal = list(set(rmap.values()))
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
            print(self[dimension].unique())
            self.uniqueValues[dimension] = self[dimension].unique()
            self.cardinality[dimension] = len(self.uniqueValues[dimension])
