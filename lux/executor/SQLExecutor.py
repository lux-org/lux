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
                    #if (spec.attribute=="Record"):
                        #if ('index' not in ldf.columns):
                            #view.data.reset_index(level=0, inplace=True)
                        #attributes.add("index")
                    #else:
                    attributes.add(spec.attribute)
            if (view.mark =="bar" or view.mark =="line"):
                SQLExecutor.executeAggregate(view, ldf)
            elif (view.mark =="histogram"):
                SQLExecutor.executeBinning(view, ldf)

    @staticmethod
    def executeAggregate(view, ldf):
        import pandas as pd
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
            #barchart case, need count data for each group
            if (measureAttr.attribute=="Record"):
                whereClause, filterVars = SQLExecutor.executeFilter(view)
                countQuery = "SELECT {}, COUNT({}) FROM {} {} GROUP BY {}".format(groupbyAttr.attribute, groupbyAttr.attribute, ldf.table_name, whereClause, groupbyAttr.attribute)
                view.data = pd.read_sql(countQuery, ldf.SQLconnection)
                view.data = view.data.rename(columns={"count":"Record"})
                view.data = utils.pandasToLux(view.data)
                print(type(view.data), view.data)

            else:
                whereClause, filterVars = SQLExecutor.executeFilter(view)
                if aggFunc == "mean":
                    meanQuery = "SELECT {}, AVG({}) as {} FROM {} {} GROUP BY {}".format(groupbyAttr.attribute, measureAttr.attribute, measureAttr.attribute, ldf.table_name, whereClause, groupbyAttr.attribute)
                    view.data = pd.read_sql(meanQuery, ldf.SQLconnection)
                    view.data = utils.pandasToLux(view.data)
    @staticmethod
    def executeBinning(view, ldf):
        import numpy as np
        import pandas as pd # is this import going to be conflicting with LuxDf?
        binAttribute = list(filter(lambda x: x.binSize!=0,view.specLst))[0]
        numBins = binAttribute.binSize
        attrMin = min(ldf.uniqueValues[binAttribute.attribute])
        attrMax = max(ldf.uniqueValues[binAttribute.attribute])
        attrType = type(ldf.uniqueValues[binAttribute.attribute][0])

        #need to calculate the bin edges before querying for the relevant data
        binWidth = (attrMax-attrMin)/numBins
        upperEdges = []
        for e in range(1, numBins):
            currEdge = attrMin + e*binWidth
            if attrType == int:
                upperEdges.append(str(math.ceil(currEdge)))
            else:
                upperEdges.append(str(currEdge))
        upperEdges = ",".join(upperEdges)
        viewFilter, filterVars = SQLExecutor.executeFilter(view)
        binCountQuery = "SELECT width_bucket, COUNT(width_bucket) FROM (SELECT width_bucket({}, '{}') FROM {}) as Buckets GROUP BY width_bucket ORDER BY width_bucket".format(binAttribute.attribute, '{'+upperEdges+'}', ldf.table_name)
        binCountData = pd.read_sql(binCountQuery, ldf.SQLconnection)

        #counts,binEdges = np.histogram(ldf[binAttribute.attribute],bins=binAttribute.binSize)
        #binEdges of size N+1, so need to compute binCenter as the bin location
        upperEdges = [float(i) for i in upperEdges.split(",")] 
        if attrType == int:
            binCenters = np.array([math.ceil((attrMin+attrMin+binWidth)/2)])
        else:
            binCenters = np.array([(attrMin+attrMin+binWidth)/2])
        binCenters = np.append(binCenters, np.mean(np.vstack([upperEdges[0:-1],upperEdges[1:]]), axis=0))
        if attrType == int:
            binCenters = np.append(binCenters, math.ceil((upperEdges[len(upperEdges)-1]+attrMax)/2))
        else:
            binCenters = np.append(binCenters, (upperEdges[len(upperEdges)-1]+attrMax)/2)
        # TODO: Should view.data be a LuxDataFrame or a Pandas DataFrame?
        view.data = pd.DataFrame(np.array([binCenters,list(binCountData['count'])]).T,columns=[binAttribute.attribute, "Count of Records (binned)"])
        view.data = utils.pandasToLux(view.data)
        
    @staticmethod
    #takes in a view and returns an appropriate SQL WHERE clause that based on the filters specified in the view's specLst
    def executeFilter(view):
        whereClause = []
        filters = utils.getFilterSpecs(view.specLst)
        filterVars = []
        if (filters):
            for f in range(0,len(filters)):
                if f == 0:
                    whereClause.append("WHERE")
                else:
                    whereClause.append("AND")
                whereClause.extend([filters[f].attribute, filters[f].filterOp, "'" + filters[f].value + "'"])
                if filters[f].attribute not in filterVars:
                    filterVars.append(filters[f].attribute)
        if whereClause == []:
            return("", [])
        else:
            whereClause = " ".join(whereClause)
        return(whereClause, filterVars)