import pandas
from lux.view.ViewCollection import ViewCollection
from lux.view.View import View
from lux.luxDataFrame.LuxDataframe import LuxDataFrame
from lux.executor.Executor import Executor
from lux.utils import utils
class PandasExecutor(Executor):
    def __init__(self):
        self.name = "PandasExecutor"

    def __repr__(self):
        return f"<PandasExecutor>"
    @staticmethod
    def execute(viewCollection:ViewCollection, ldf:LuxDataFrame):
        '''
        Given a ViewCollection, fetch the data required to render the view
        1) Apply filters
        2) Retreive relevant attribute
        3) return a DataFrame with relevant results
        '''
        for view in viewCollection:
            PandasExecutor.executeFilter(view, ldf)
            # Select relevant data based on attribute information
            attributes = set([])
            for spec in view.specLst:
                if (spec.attribute):
                    if (spec.attribute!="Record"):
                        attributes.add(spec.attribute)
            if len(ldf) > 10000:
                view.data = view.data[list(attributes)].sample(n = 10000, random_state = 1)
            else:
                view.data = view.data[list(attributes)]
            if (view.mark =="bar" or view.mark =="line"):
                PandasExecutor.executeAggregate(view, ldf)
            elif (view.mark =="histogram"):
                PandasExecutor.executeBinning(view, ldf)

    @staticmethod
    def executeAggregate(view: View, ldf: LuxDataFrame):
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
                view.data = view.data.reset_index()
                view.data = view.data.groupby(groupbyAttr.attribute).count().reset_index()
                view.data = view.data.rename(columns={"index":"Record"})

            else:
                groupbyResult = view.data.groupby(groupbyAttr.attribute)
                view.data = groupbyResult.agg(aggFunc).reset_index()
    @staticmethod
    def executeBinning(view, ldf):
        import numpy as np
        import pandas as pd # is this import going to be conflicting with LuxDf?
        binAttribute = list(filter(lambda x: x.binSize!=0,view.specLst))[0]
        #TODO:binning runs for name attribte. Name attribute has datatype quantitative which is wrong.
        counts,binEdges = np.histogram(ldf[binAttribute.attribute],bins=binAttribute.binSize)
        #binEdges of size N+1, so need to compute binCenter as the bin location
        binCenter = np.mean(np.vstack([binEdges[0:-1],binEdges[1:]]), axis=0)
        # TODO: Should view.data be a LuxDataFrame or a Pandas DataFrame?
        view.data = pd.DataFrame(np.array([binCenter,counts]).T,columns=[binAttribute.attribute, "Count of Records (binned)"])        
        
    @staticmethod
    def executeFilter(view, ldf):
        filters = utils.getFilterSpecs(view.specLst)
        if (filters):
            # TODO: Need to handle OR logic
            for filter in filters:
                view.data = PandasExecutor.applyFilter(ldf,filter.attribute,filter.filterOp,filter.value)
        else:
            view.data = ldf
    
    @staticmethod
    def applyFilter(df: pandas.DataFrame, attribute:str, op: str, val: object) -> pandas.DataFrame:
        """
        Helper function for applying filter to a dataframe
        
        Parameters
        ----------
        df : pandas.DataFrame
            Dataframe to filter on
        attribute : str
            Filter attribute
        op : str
            Filter operation, '=', '<', '>', '<=', '>=', '!='
        val : object
            Filter value 
        
        Returns
        -------
        pandas.DataFrame
            Dataframe resulting from the filter operation
        """        
        if (op == '='):
            return df[df[attribute] == val]
        elif (op == '<'):
            return df[df[attribute] < val]
        elif (op == '>'):
            return df[df[attribute] > val]
        elif (op == '<='):
            return df[df[attribute] <= val]
        elif (op == '>='):
            return df[df[attribute] >= val]
        elif (op == '!='):
            return df[df[attribute] != val]
        return df