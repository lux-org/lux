import pandas
from lux.view.ViewCollection import ViewCollection
from lux.view.View import View
from lux.luxDataFrame.LuxDataframe import LuxDataFrame
from lux.executor.Executor import Executor
from lux.utils import utils
import psycopg2
import math

class SQLExecutor(Executor):
    def __init__(self):
        self.name = "Executor"
        self.selection = []
        self.tables = []
        self.filters = ""

    def __repr__(self):
        return f"<Executor>"
    @staticmethod
    def execute(viewCollection:ViewCollection, ldf):
        '''
        Given a ViewCollection, fetch the data required to render the view
        1) Apply filters
        2) Retreive relevant attribute
        3) return a DataFrame with relevant results
        '''
        for view in viewCollection:
            Executor.executeFilter(view, ldf)
            # Select relevant data based on attribute information
            attributes = set([])
            for spec in view.specLst:
                if (spec.attribute):
                    if (spec.attribute=="Record"):
                        if ('index' not in view.data.columns):
                            view.data.reset_index(level=0, inplace=True)
                        attributes.add("index")
                    else:
                        attributes.add(spec.attribute)
            view.data = view.data[list(attributes)]
            if (view.mark =="bar" or view.mark =="line"):
                Executor.executeAggregate(view, ldf)
            elif (view.mark =="histogram"):
                Executor.executeBinning(view, ldf)

    @staticmethod
    def executeAggregate(view, ldf):
        # TODO (Jaywoo)
        # get attribute
        # aggreagte in spec
        # horsepower by origin -> lux.spec(horsepower,aggregate = "mean") lux.spec(attribute = Origin)
        # need to add aggregate spec in the compiling stage(inside compiler.determinEncoding)
        xAttr = view.getObjFromChannel("x")[0]
        yAttr = view.getObjFromChannel("y")[0]
        
        groupbyAttr =""
        measureAttr =""
        if (yAttr.aggregation!=""):
            groupbyAttr = xAttr
            measureAttr = yAttr
            aggFunc = yAttr.aggregation
        if (xAttr.aggregation!=""):
            groupbyAttr = yAttr
            measureAttr = xAttr
            aggFunc = xAttr.aggregation
        
        if (measureAttr!=""):
            if (measureAttr.attribute=="Record"):
                countSeries = view.data.groupby(groupbyAttr.attribute).count().iloc[:,0]
                countSeries.name = "Record"
                view.data = countSeries.to_frame().reset_index()
            else:
                groupbyResult = view.data.groupby(groupbyAttr.attribute)
                view.data = groupbyResult.agg(aggFunc).reset_index()
    @staticmethod
    def executeBinning(view, ldf):
        import numpy as np
        import pandas as pd # is this import going to be conflicting with LuxDf?
        binAttribute = list(filter(lambda x: x.binSize!=0,view.specLst))[0]
        numBins = binAttribute.binSize
        attrMin = min(ldf.uniqueValues[binAttribute.attribute])
        attrMax = max(ldf.uniqueValues[binAttribute.attribute])
        attrType = type(ldf.uniqueValues[binAttribute.attribute][0])

        binWidth = (attrMax-attrMin)/numBins
        upperEdges = []
        for e in range(1, numBins):
            currEdge = attrMin + e*binWidth
            if attrType == int:
                upperEdges.append(str(math.ceil(currEdge)))
            else:
                upperEdges.append(str(currEdge))
        upperEdges = ",".join(upperEdges)
        viewFilter = SQLExecutor.executeFilter(view)
        print(viewFilter)
        binCountQuery = "SELECT COUNT(width_bucket) FROM (SELECT width_bucket({}, '{}') FROM {}) as Buckets GROUP BY width_bucket".format(binAttribute.attribute, '{'+upperEdges+'}', ldf.table_name)
        binCountData = pd.read_sql(binCountQuery, ldf.SQLconnection)

        #counts,binEdges = np.histogram(ldf[binAttribute.attribute],bins=binAttribute.binSize)
        #binEdges of size N+1, so need to compute binCenter as the bin location
        upperEdges = [float(i) for i in upperEdges.split(",")] 
        print(upperEdges)
        if attrType == int:
            binCenters = np.array([math.ceil((attrMin+binWidth)/2)])
        else:
            binCenters = np.array([(attrMin+binWidth)/2])
        binCenters = np.append(binCenters, np.mean(np.vstack([upperEdges[0:-1],upperEdges[1:]]), axis=0))
        if attrType == int:
            binCenters = np.append(binCenters, math.ceil((upperEdges[len(upperEdges)-1]+attrMax)/2))
        else:
            binCenters = np.append(binCenters, (upperEdges[len(upperEdges)-1]+attrMax)/2)
        print(binCenters)
        # TODO: Should view.data be a LuxDataFrame or a Pandas DataFrame?
        view.data = pd.DataFrame(np.array([binCenters,list(binCountData['count'])]).T,columns=[binAttribute.attribute, "Count of Records (binned)"])
        print(view.data)    
        
    @staticmethod
    #takes in a view and returns an appropriate SQL WHERE clause that based on the filters specified in the view's specLst
    def executeFilter(view):
        whereClause = []
        filters = utils.getFilterSpecs(view.specLst)
        print(filters)
        if (filters):
            for f in range(0,len(filters)):
                if f == 0:
                    whereClause.append("WHERE")
                else:
                    whereClause.append("AND")
                whereClause.extend([filters[f].attribute, filters[f].filterOp, "'" + filters[f].value + "'"])
        whereClause = " ".join(whereClause)
        return(whereClause)