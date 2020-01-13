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

        # def __str__(self):
        # 	vis = self.display()
        # 	if (vis):
        # 		return vis
        # 	else:
        # 		return f"<Data Obj: {str(self.dataset)} -- {str(self.spec)}>"

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

    # TODO: move to global class method when there is an overall module for API
    # def fromDataFrame(df):
    # 	'''
    #	Example
    # 	import pandas as pd
    # 	df = pd.read_csv("data/cars.csv")
    # 	[name of package].fromDataFrame(df)
    #   e.g. pd.Dataframe
    # 	'''
    # 	from dataset.Dataset import Dataset
    # 	dataset = Dataset(df = df)
    # 	return DataObj(dataset)
    # Mappers to Action classes

    # TODO: move to global class method when there is an overall module for API
    # def fromDataFrame(df):
    # 	'''
    #	Example
    # 	import pandas as pd
    # 	df = pd.read_csv("data/cars.csv")
    # 	[name of package].fromDataFrame(df)
    #   e.g. pd.Dataframe
    # 	'''
    # 	from dataset.Dataset import Dataset
    # 	dataset = Dataset(df = df)
    # 	return DataObj(dataset)
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
        if (type(self.compiled).__name__ == "DataObj"):
            dobj_dict["currentView"] = self.compiled.renderVSpec()
        if (type(self.compiled).__name__ == "DataObjCollection"):
            # if the compiled object is a collection, see if we can remove the elements with "?" and generate a Current View
            specifiedDobj = self.getVariableFieldsRemoved()
            if (specifiedDobj.spec!=[]): specifiedDobj.compile(enumerateCollection=False)
            if (currentView!=""):
                dobj_dict["currentView"] = currentView.compiled.renderVSpec()
            elif (specifiedDobj.isEmpty()):
                dobj_dict["currentView"] = {}
            else:
                specifiedDobj.compile(enumerateCollection=False)
                dobj_dict["currentView"] = specifiedDobj.compiled.renderVSpec()
            if (self.recommendation=={}):
                self.recommendation = {"action": "Vis Collection",
                    "collection":self.compiled
                }
        # Recommended Collection
        dobj_dict["recommendations"] = []
        import copy
        recCopy= copy.copy(self.recommendation)
        if (recCopy != {}):
            recCopy["vspec"] = []
            for vis in recCopy["collection"].collection:
                chart = vis.renderVSpec()
                recCopy["vspec"].append(chart)
            dobj_dict["recommendations"].append(recCopy)
            # delete DataObjectCollection since not JSON serializable
            del dobj_dict["recommendations"][0]["collection"]
        return dobj_dict

    def display(self, renderer="altair", currentView=""):
        # render this data object as: vis, columns, etc.?
        # import widgetDisplay
        # if (renderer=="altair"):
        # 	renderer = AltairRenderer()
        # chart = renderer.createVis(self.compiled)
        # widget = widgetDisplay.Mockup(graphSpecs = [chart.to_dict()])
        # return widget
        # return chart
        import displayWidget
        widgetJSON = self.toJSON(currentView=currentView)
        widget = displayWidget.DisplayWidget(
            # data=json.loads(self.dataset.df.to_json(orient='records')),
            currentView=widgetJSON["currentView"],
            recommendations=widgetJSON["recommendations"]
        )
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
    def preprocess(self):
        from lux.service.patternSearch import preprocessing
        preprocessing.aggregate(self)
        preprocessing.interpolate(self, 100)
        preprocessing.normalize(self)
    def similarPattern(self,query,topK=-1):
        from lux.service.patternSearch.similarityDistance import euclideanDist
        from lux.compiler.Compiler import applyDataTransformations
        result = lux.Result()
        rowSpecs = list(filter(lambda x: x.className == "Row", query.spec))
        if(len(rowSpecs) == 1):
            query.dataset = applyDataTransformations(query.dataset,rowSpecs[0].fAttribute,rowSpecs[0].fVal)
            query.preprocess()
            #for loop to create assign euclidean distance
            recommendation = {"action":"Similarity",
                                   "description":"Show other charts that are visually similar to the Current View."}
            for dobj in self.compiled.collection:
                dobj.preprocess()
                dobj.score = euclideanDist(query, dobj)
            self.compiled.normalizeScore(invertOrder=True)
            self.compiled.sort(removeInvalid=True)
            if(topK!=-1):
                self.compiled = self.compiled.topK(topK)
            recommendation["collection"] = self.compiled
            result.addResult(recommendation,dobj)
            return result
        else:
            print("Query needs to have 1 row value")
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