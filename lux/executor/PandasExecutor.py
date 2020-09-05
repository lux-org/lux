import pandas
from lux.vis.VisList import VisList
from lux.vis.Vis import Vis
from lux.core.frame import LuxDataFrame
from lux.executor.Executor import Executor
from lux.utils import utils
class PandasExecutor(Executor):
    '''
    Given a Vis objects with complete specifications, fetch and process data using Pandas dataframe operations.
    '''
    def __init__(self):
        self.name = "PandasExecutor"

    def __repr__(self):
        return f"<PandasExecutor>"
    @staticmethod
    def execute(vislist:VisList, ldf:LuxDataFrame):
        '''
        Given a VisList, fetch the data required to render the vis.
        1) Apply filters
        2) Retrieve relevant attribute
        3) Perform vis-related processing (aggregation, binning)
        4) return a DataFrame with relevant results

        Parameters
        ----------
        vislist: list[lux.Vis]
            vis list that contains lux.Vis objects for visualization.
        ldf : lux.core.frame
            LuxDataFrame with specified intent.

        Returns
        -------
        None
        '''
        for vis in vislist:
            vis._vis_data = ldf # The vis data starts off being the same as the content of the original dataframe
            filter_executed = PandasExecutor.execute_filter(vis)
            # Select relevant data based on attribute information
            attributes = set([])
            for clause in vis._inferred_intent:
                if (clause.attribute):
                    if (clause.attribute!="Record"):
                        attributes.add(clause.attribute)
            if len(vis.data) > 10000:
                vis._vis_data = vis.data[list(attributes)].sample(n = 10000, random_state = 1)
            else:
                vis._vis_data = vis.data[list(attributes)]
            if (vis.mark =="bar" or vis.mark =="line"):
                PandasExecutor.execute_aggregate(vis,isFiltered = filter_executed)
            elif (vis.mark =="histogram"):
                PandasExecutor.execute_binning(vis)

    @staticmethod
    def execute_aggregate(vis: Vis,isFiltered = True):
        '''
        Aggregate data points on an axis for bar or line charts

        Parameters
        ----------
        vis: lux.Vis
            lux.Vis object that represents a visualization
        ldf : lux.core.frame
            LuxDataFrame with specified intent.

        Returns
        -------
        None
        '''
        import numpy as np
        import pandas as pd

        x_attr = vis.get_attr_by_channel("x")[0]
        y_attr = vis.get_attr_by_channel("y")[0]
        has_color = False
        groupby_attr =""
        measure_attr =""
        if (x_attr.aggregation is None or y_attr.aggregation is None):
            return
        if (y_attr.aggregation!=""):
            groupby_attr = x_attr
            measure_attr = y_attr
            agg_func = y_attr.aggregation
        if (x_attr.aggregation!=""):
            groupby_attr = y_attr
            measure_attr = x_attr
            agg_func = x_attr.aggregation
        if (groupby_attr.attribute in vis.data.unique_values.keys()):
            attr_unique_vals = vis.data.unique_values[groupby_attr.attribute]
        #checks if color is specified in the Vis
        if len(vis.get_attr_by_channel("color")) == 1:
            color_attr = vis.get_attr_by_channel("color")[0]
            color_attr_vals = vis.data.unique_values[color_attr.attribute]
            color_cardinality = len(color_attr_vals)
            #NOTE: might want to have a check somewhere to not use categorical variables with greater than some number of categories as a Color variable----------------
            has_color = True
        else:
            color_cardinality = 1
        
        if (measure_attr!=""):
            if (measure_attr.attribute=="Record"):
                vis._vis_data = vis.data.reset_index()
                #if color is specified, need to group by groupby_attr and color_attr
                if has_color:
                    vis._vis_data = vis.data.groupby([groupby_attr.attribute, color_attr.attribute]).count().reset_index()
                    vis._vis_data = vis.data.rename(columns={"index":"Record"})
                    vis._vis_data = vis.data[[groupby_attr.attribute,color_attr.attribute,"Record"]]
                else:
                    vis._vis_data = vis.data.groupby(groupby_attr.attribute).count().reset_index()
                    vis._vis_data = vis.data.rename(columns={"index":"Record"})
                    vis._vis_data = vis.data[[groupby_attr.attribute,"Record"]]
            else:
                #if color is specified, need to group by groupby_attr and color_attr
                if has_color:
                    groupby_result = vis.data.groupby([groupby_attr.attribute, color_attr.attribute])
                else:
                    groupby_result = vis.data.groupby(groupby_attr.attribute)
                groupby_result = groupby_result.agg(agg_func)
                intermediate = groupby_result.reset_index()
                vis._vis_data = intermediate.__finalize__(vis.data)
            result_vals = list(vis.data[groupby_attr.attribute])
            #create existing group by attribute combinations if color is specified
            #this is needed to check what combinations of group_by_attr and color_attr values have a non-zero number of elements in them
            if has_color:
                res_color_combi_vals = []
                result_color_vals = list(vis.data[color_attr.attribute])
                for i in range(0, len(result_vals)):
                    res_color_combi_vals.append([result_vals[i], result_color_vals[i]])
            # For filtered aggregation that have missing groupby-attribute values, set these aggregated value as 0, since no datapoints
            if (isFiltered or has_color and attr_unique_vals):
                N_unique_vals = len(attr_unique_vals)
                if (len(result_vals) != N_unique_vals*color_cardinality):    
                    columns = vis.data.columns
                    if has_color:
                        df = pd.DataFrame({columns[0]: attr_unique_vals*color_cardinality, columns[1]: pd.Series(color_attr_vals).repeat(N_unique_vals)})
                        vis._vis_data = vis.data.merge(df, on=[columns[0],columns[1]], how='right', suffixes=['', '_right'])
                        for col in columns[2:]:
                            vis.data[col] = vis.data[col].fillna(0) #Triggers __setitem__
                        assert len(list(vis.data[groupby_attr.attribute])) == N_unique_vals*len(color_attr_vals), f"Aggregated data missing values compared to original range of values of `{groupby_attr.attribute, color_attr.attribute}`."
                        vis._vis_data = vis.data.iloc[:,:3] # Keep only the three relevant columns not the *_right columns resulting from merge
                    else:
                        df = pd.DataFrame({columns[0]: attr_unique_vals})
                        
                        vis._vis_data = vis.data.merge(df, on=columns[0], how='right', suffixes=['', '_right'])

                        for col in columns[1:]:
                            vis.data[col] = vis.data[col].fillna(0)
                        assert len(list(vis.data[groupby_attr.attribute])) == N_unique_vals, f"Aggregated data missing values compared to original range of values of `{groupby_attr.attribute}`."
            vis._vis_data = vis.data.sort_values(by=groupby_attr.attribute, ascending=True)
            vis._vis_data = vis.data.reset_index()
            vis._vis_data = vis.data.drop(columns="index")

    @staticmethod
    def execute_binning(vis: Vis):
        '''
        Binning of data points for generating histograms

        Parameters
        ----------
        vis: lux.Vis
            lux.Vis object that represents a visualization
        ldf : lux.core.frame
            LuxDataFrame with specified intent.

        Returns
        -------
        None
        '''
        import numpy as np
        import pandas as pd # is this import going to be conflicting with LuxDf? 
        bin_attribute = list(filter(lambda x: x.bin_size!=0,vis._inferred_intent))[0]
        if not np.isnan(vis.data[bin_attribute.attribute]).all():
            series = vis.data[bin_attribute.attribute].dropna() # np.histogram breaks if array contain NaN
            #TODO:binning runs for name attribte. Name attribute has datatype quantitative which is wrong.
            counts,bin_edges = np.histogram(series,bins=bin_attribute.bin_size)
            #bin_edges of size N+1, so need to compute bin_center as the bin location
            bin_center = np.mean(np.vstack([bin_edges[0:-1],bin_edges[1:]]), axis=0)
            # TODO: Should vis.data be a LuxDataFrame or a Pandas DataFrame?
            vis._vis_data = pd.DataFrame(np.array([bin_center,counts]).T,columns=[bin_attribute.attribute, "Number of Records"])

    @staticmethod
    def execute_filter(vis: Vis):
        assert vis.data is not None, "execute_filter assumes input vis.data is populated (if not, populate with LuxDataFrame values)"
        filters = utils.get_filter_specs(vis._inferred_intent)
        
        if (filters):
            # TODO: Need to handle OR logic
            for filter in filters:
                vis._vis_data = PandasExecutor.apply_filter(vis.data, filter.attribute, filter.filter_op, filter.value)
            return True
        else:
            return False
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