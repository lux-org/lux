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
    def execute(view_collection:ViewCollection, ldf:LuxDataFrame):
        '''
        Given a ViewCollection, fetch the data required to render the view.
        1) Apply filters
        2) Retrieve relevant attribute
        3) Perform vis-related processing (aggregation, binning)
        4) return a DataFrame with relevant results

        Parameters
		----------
		view_collection: list[lux.View]
		    view collection that contains lux.View objects for visualization.
		ldf : lux.luxDataFrame.LuxDataFrame
			LuxDataFrame with specified context.

        Returns
		-------
		None
        '''
        for view in view_collection:
            view.data = ldf # The view data starts off being the same as the content of the original dataframe
            PandasExecutor.execute_filter(view)
            # Select relevant data based on attribute information
            attributes = set([])
            for spec in view.spec_lst:
                if (spec.attribute):
                    if (spec.attribute!="Record"):
                        attributes.add(spec.attribute)
            if len(view.data) > 10000:
                view.data = view.data[list(attributes)].sample(n = 10000, random_state = 1)
            else:
                view.data = view.data[list(attributes)]
            if (view.mark =="bar" or view.mark =="line"):
                PandasExecutor.execute_aggregate(view)
            elif (view.mark =="histogram"):
                PandasExecutor.execute_binning(view)

    @staticmethod
    def execute_aggregate(view: View):
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
        x_attr = view.get_attr_by_channel("x")[0]
        y_attr = view.get_attr_by_channel("y")[0]
        groupby_attr =""
        measure_attr =""
        if (y_attr.aggregation!=""):
            groupby_attr = x_attr
            measure_attr = y_attr
            agg_func = y_attr.aggregation
        if (x_attr.aggregation!=""):
            groupby_attr = y_attr
            measure_attr = x_attr
            agg_func = x_attr.aggregation
        all_attr_vals = view.data.unique_values[groupby_attr.attribute]
        if (measure_attr!=""):
            if (measure_attr.attribute=="Record"):
                view.data = view.data.reset_index()
                view.data = view.data.groupby(groupby_attr.attribute).count().reset_index()
                view.data = view.data.rename(columns={"index":"Record"})
                view.data = view.data[[groupby_attr.attribute,"Record"]]
            else:
                groupby_result = view.data.groupby(groupby_attr.attribute)
                view.data = groupby_result.agg(agg_func).reset_index()
            result_vals = list(view.data[groupby_attr.attribute])
            if (len(result_vals) != len(all_attr_vals)):
                # For filtered aggregation that have missing groupby-attribute values, set these aggregated value as 0, since no datapoints
                for vals in all_attr_vals:
                    if (vals not in result_vals):
                        view.data.loc[len(view.data)] = [vals]+[0]*(len(view.data.columns)-1)
            assert len(list(view.data[groupby_attr.attribute])) == len(all_attr_vals), f"Aggregated data missing values compared to original range of values of `{groupby_attr.attribute}`."
            view.data = view.data.sort_values(by=groupby_attr.attribute, ascending=True)
            view.data = view.data.reset_index()
            view.data = view.data.drop(columns="index")

    @staticmethod
    def execute_binning(view: View):
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
        bin_attribute = list(filter(lambda x: x.bin_size!=0,view.spec_lst))[0]
        #TODO:binning runs for name attribte. Name attribute has datatype quantitative which is wrong.
        counts,bin_edges = np.histogram(view.data[bin_attribute.attribute],bins=bin_attribute.bin_size)
        #bin_edges of size N+1, so need to compute bin_center as the bin location
        bin_center = np.mean(np.vstack([bin_edges[0:-1],bin_edges[1:]]), axis=0)
        # TODO: Should view.data be a LuxDataFrame or a Pandas DataFrame?
        view.data = pd.DataFrame(np.array([bin_center,counts]).T,columns=[bin_attribute.attribute, "Count of Records"])
        
    @staticmethod
    def execute_filter(view: View):
        assert view.data is not None, "execute_filter assumes input view.data is populated (if not, populate with LuxDataFrame values)"
        filters = utils.get_filter_specs(view.spec_lst)
        
        if (filters):
            # TODO: Need to handle OR logic
            for filter in filters:
                view.data = PandasExecutor.apply_filter(view.data, filter.attribute, filter.filter_op, filter.value)
    @staticmethod
    def apply_filter(df: pandas.DataFrame, attribute:str, op: str, val: object) -> pandas.DataFrame:
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