import pandas
from lux.view.ViewCollection import ViewCollection
from lux.view.View import View
from lux.luxDataFrame.LuxDataframe import LuxDataFrame
from lux.executor.Executor import Executor
from lux.utils import utils
class PandasExecutor(Executor):
    '''
    Given a View objects with complete specifications, fetch and process data using Pandas dataframe operations.
    '''
    def __init__(self):
        self.name = "PandasExecutor"

    def __repr__(self):
        return f"<PandasExecutor>"
    @staticmethod
    def execute(viewCollection:ViewCollection, ldf:LuxDataFrame):
        '''
        Given a ViewCollection, fetch the data required to render the view.
        1) Apply filters
        2) Retrieve relevant attribute
        3) Perform vis-related processing (aggregation, binning)
        4) return a DataFrame with relevant results

        Parameters
		----------
		viewCollection: list[lux.View]
		    view collection that contains lux.View objects for visualization.
		ldf : lux.luxDataFrame.LuxDataFrame
			LuxDataFrame with specified context.

        Returns
		-------
		None
        '''
        for view in viewCollection:
            view.data = ldf # The view data starts off being the same as the content of the original dataframe
            PandasExecutor.executeFilter(view)
            # Select relevant data based on attribute information
            attributes = set([])
            for spec in view.specLst:
                if (spec.attribute):
                    if (spec.attribute!="Record"):
                        attributes.add(spec.attribute)
            if len(view.data) > 10000:
                view.data = view.data[list(attributes)].sample(n = 10000, random_state = 1)
            else:
                view.data = view.data[list(attributes)]
            if (view.mark =="bar" or view.mark =="line"):
                PandasExecutor.executeAggregate(view)
            elif (view.mark =="histogram"):
                PandasExecutor.executeBinning(view)

    @staticmethod
    def executeAggregate(view: View):
        '''
        Aggregate data points on an axis for bar or line charts

        Parameters
        ----------
        view: lux.View
            lux.View object that represents a visualization
        ldf : lux.luxDataFrame.LuxDataFrame
            LuxDataFrame with specified context.

        Returns
        -------
        None
        '''
        import numpy as np
        xAttr = view.getAttrByChannel("x")[0]
        yAttr = view.getAttrByChannel("y")[0]
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
        arr_s = [x for x in view.data.uniqueValues[groupbyAttr.attribute]]

        if (measureAttr!=""):
            if (measureAttr.attribute=="Record"):
                view.data = view.data.reset_index()
                view.data = view.data.groupby(groupbyAttr.attribute).count().reset_index()
                view.data = view.data.rename(columns={"index":"Record"})
            else:
                groupbyResult = view.data.groupby(groupbyAttr.attribute)
                view.data = groupbyResult.agg(aggFunc).reset_index()
            result = [x for x in view.data[groupbyAttr.attribute]]
            if (len(result) != len(arr_s)):
                s = False
                for index in range(len(arr_s)):
                    if (arr_s[index] not in result):
                        s = True
                        size = len(view.data.columns) - 1
                        view.data.loc[arr_s[index]] = [arr_s[index]] + [0] * size
                if (s == True):
                    view.data = view.data.reset_index()
                    view.data = view.data.drop(columns="index")
            view.data = view.data.sort_values(by=groupbyAttr.attribute, ascending=True)
            view.data = view.data.reset_index()
            view.data = view.data.drop(columns="index")

    @staticmethod
    def executeBinning(view: View):
        '''
        Binning of data points for generating histograms

        Parameters
        ----------
        view: lux.View
            lux.View object that represents a visualization
        ldf : lux.luxDataFrame.LuxDataFrame
            LuxDataFrame with specified context.

        Returns
        -------
        None
        '''
        import numpy as np
        import pandas as pd # is this import going to be conflicting with LuxDf?
        binAttribute = list(filter(lambda x: x.binSize!=0,view.specLst))[0]
        #TODO:binning runs for name attribte. Name attribute has datatype quantitative which is wrong.
        counts,binEdges = np.histogram(view.data[binAttribute.attribute],bins=binAttribute.binSize)
        #binEdges of size N+1, so need to compute binCenter as the bin location
        binCenter = np.mean(np.vstack([binEdges[0:-1],binEdges[1:]]), axis=0)
        # TODO: Should view.data be a LuxDataFrame or a Pandas DataFrame?
        view.data = pd.DataFrame(np.array([binCenter,counts]).T,columns=[binAttribute.attribute, "Count of Records (binned)"])        
        
    @staticmethod
    def executeFilter(view: View):
        assert view.data is not None, "executeFilter assumes input view.data is populated (if not, populate with LuxDataFrame values)"
        filters = utils.getFilterSpecs(view.specLst)
        
        if (filters):
            # TODO: Need to handle OR logic
            for filter in filters:
                view.data = PandasExecutor.applyFilter(view.data,filter.attribute,filter.filterOp,filter.value)    
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
        df: pandas.DataFrame
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