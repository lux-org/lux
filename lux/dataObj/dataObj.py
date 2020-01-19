from lux.dataObj.Row import Row
from lux.dataObj.Column import Column

import lux
from lux.vizLib.altair.AltairRenderer import AltairRenderer
from lux.compiler.Compiler import Compiler
import json


class DataObj:
    '''
    DataObj is an abstract object representing some aspect of the data.
    This can be based on what the user has specified or what is created as outputs.
    It can be a visualization, group of data points, column, etc and does not have to be fully specified.
    '''
    def __init__(self, dataset, spec=[], title=""):
        self.dataset = dataset  # may be inefficient use of memory
        self.transformedDataset = dataset
        self.spec = spec  # list of Row and Column objects
        self.title = title
        self.type = ""
        self.mark = ""
        self.score = -1
        self.recommendations = [] # for the Result recommendations
        self.recommendation = {} # for the display() and toJSON() in DataObj
        self.compile()

    def __repr__(self):
        # TODO: figure out a way to call display when printing out a data obj
        # currently repr can not be used for printing out non-string values. (Ref to how Dataframe is displayed by default in Pandas)
        if self.score != -1:
            return f"<Data Obj: {str(self.spec)} -- {self.score:.2f}>"
        else:
            return f"<Data Obj: {str(self.spec)}>"

    def compile(self, enumerateCollection=True):
        dobj = self
        compiler = Compiler()
        # 1. If the DataObj represent a collection, then compile it into a collection. Otherwise, return False
        # Input: DataObj --> Output: DataObjCollection/False
        if (enumerateCollection):
            dataObjCollection = compiler.enumerateCollection(dobj)
        else:
            dataObjCollection = False
        # 2. For every DataObject in the DataObject Collection, expand underspecified
        # Output : DataObj/DataObjectCollection
        if (dataObjCollection):
            self.compiled = dataObjCollection  # Preserve any dataObjectCollection specification
            compiledCollection = []
            for dataObj in dataObjCollection.collection:
                compiled = compiler.expandUnderspecified(dataObj)  # autofill data type/model information
                compiled = compiler.determineEncoding(compiled)  # autofill viz related information
                compiledCollection.append(compiled)
            # print ("uncompiled:",dataObj)
            # print ("compiled:",compiled)
            self.compiled.collection = compiledCollection  # return DataObjCollection
        else:
            compiled = compiler.expandUnderspecified(dobj)  # autofill data type/model information
            compiled = compiler.determineEncoding(compiled)  # autofill viz related information
            self.compiled = compiled
        # print ("uncompiled:",dobj)
        # print ("compiled:",self.compiled)

    def renderVSpec(self, renderer="altair"):
        from lux.vizLib.altair.AltairRenderer import AltairRenderer
        if (renderer == "altair"):
            renderer = AltairRenderer()
        return renderer.createVis(self)

    def isEmpty(self):
        return self.spec == []

    def singleDisplay(self, renderer="altair"):
        # For debugging only:
        # display not through widget but through altair default
        if (renderer == "altair"):
            renderer = AltairRenderer()
        chart = renderer.createVis(self.compiled)
        return chart

    def getObjByRowColType(self, rowColType):
        specObj = list(filter(lambda x: x.className == rowColType, self.spec))
        return specObj

    def getObjFromChannel(self, channel):
        specObj = list(filter(lambda x: x.channel == channel if hasattr(x, "channel") else False, self.spec))
        return specObj

    def getObjByDataModel(self, dmodel):
        return list(filter(lambda x: x.dataModel == dmodel if hasattr(x, "dataModel") else False, self.spec))

    def getByColumnName(self, columnName):
        return list(filter(lambda x: x.columnName == columnName, self.spec))

    def removeColumnFromSpec(self, columnName):
        self.spec = list(filter(lambda x: x.columnName != columnName, self.spec))

    def removeColumnFromSpecNew(self, columnName):
        newSpec = []
        for i in range(0, len(self.spec)):
            if isinstance(self.spec[i], Column):
                columnSpec = []
                columnNames = self.spec[i].columnName
                # if only one variable in a column, columnName results in a string and not a list so
                # you need to differentiate the cases
                if isinstance(columnNames, list):
                    for column in columnNames:
                        if column != columnName:
                            columnSpec.append(column)
                    newSpec.append(Column(columnSpec))
                else:
                    if columnNames != columnName:
                        newSpec.append(Column(columnNames))
            else:
                newSpec.append(self.spec[i])
        self.spec = newSpec

    def getVariableFieldsRemoved(self):
        # remove fields that either have a wildcard or is a list
        import copy
        withoutWildmarkCopy = copy.deepcopy(self)
        for spec in withoutWildmarkCopy.spec[:]: # make a copy of list while iterating
            if isinstance(spec, Column):
                if (spec.columnName == "?" or isinstance(spec.columnName, list)):
                    withoutWildmarkCopy.spec.remove(spec)
            elif isinstance(spec, Row):
                if (spec.fVal == "?"):
                    withoutWildmarkCopy.spec.remove(spec)
        return withoutWildmarkCopy

    # Mappers to Action classes
    def correlation(self):
        from lux.action.Correlation import correlation
        return correlation(self)

    def distribution(self):
        from lux.action.Distribution import distribution
        return distribution(self)

    def generalize(self):
        from lux.action.Generalize import generalize
        return generalize(self)

    def toJSON(self,currentView=""):
        dobj_dict = {}
        # Current View (if any)
        dobj_dict["currentView"] = lux.Result.currentViewToJSON(self,currentView)
        # Recommended Collection
        if (type(self.compiled).__name__ == "DataObjCollection"):
            if (self.recommendation=={}):
                self.recommendation = {"action": "Vis Collection",
                    "collection":self.compiled
                }
        dobj_dict["recommendations"] = lux.Result.recToJSON(self.recommendation)
        return dobj_dict
    
    def display(self, renderer="altair", currentView=""):
        widget = lux.Result.display(self,renderer=renderer,currentView=currentView)
        return widget
        
    def filter(self):
        from lux.action.Filter import filter
        return filter(self)

    def enhance(self):
        from lux.action.Enhance import enhance
        return enhance(self)
    def overview(self):
        dataset = self.dataset
        from lux.action.Distribution import distribution
        dobj = lux.DataObj(dataset,[lux.Column("?",dataModel="measure")])
        result = dobj.distribution()

        from lux.action.Correlation import correlation
        dobj = lux.DataObj(dataset,[lux.Column("?",dataModel="measure"),lux.Column("?",dataModel="measure")])
        result2 = dobj.correlation()

        # Merge the two Result object from the two actions
        result.mergeResult(result2)
        return result
    def similarPattern(self,query,topK=-1):
        from lux.action.Similarity import similarPattern
        return similarPattern(self,query,topK)
    
    def showMore(self):
        currentViewExist = self.compiled.spec!=[]
        result = lux.Result()
        if (currentViewExist):
            result.mergeResult(self.enhance())
            result.mergeResult(self.filter())
            result.mergeResult(self.generalize())
        else: 
            result.mergeResult(self.overview())
        return result