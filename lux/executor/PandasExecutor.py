import pandas
from lux.vis.VisList import VisList
from lux.vis.Vis import Vis
from lux.luxDataFrame.LuxDataframe import LuxDataFrame
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
    def execute(view_collection:VisList, ldf:LuxDataFrame):
        '''
        Given a VisList, fetch the data required to render the view.
        1) Apply filters
        2) Retrieve relevant attribute
        3) Perform vis-related processing (aggregation, binning)
        4) return a DataFrame with relevant results

        Parameters
        ----------
        view_collection: list[lux.Vis]
            vis list that contains lux.Vis objects for visualization.
        ldf : lux.luxDataFrame.LuxDataFrame
            LuxDataFrame with specified intent.

        Returns
        -------
        None
        '''
        for view in view_collection:
            view.data = ldf # The view data starts off being the same as the content of the original dataframe
            filter_executed = PandasExecutor.execute_filter(view)
            # Select relevant data based on attribute information
            attributes = set([])
            for clause in view._inferred_intent:
                if (clause.attribute):
                    if (clause.attribute!="Record"):
                        attributes.add(clause.attribute)
            if len(view.data) > 10000:
                view.data = view.data[list(attributes)].sample(n = 10000, random_state = 1)
            else:
                view.data = view.data[list(attributes)]
            if (view.mark =="bar" or view.mark =="line"):
                PandasExecutor.execute_aggregate(view,isFiltered = filter_executed)
            elif (view.mark =="histogram"):
                PandasExecutor.execute_binning(view)

    @staticmethod
    def execute_aggregate(view: Vis,isFiltered = True):
        '''
        Aggregate data points on an axis for bar or line charts

        Parameters
        ----------
        view: lux.Vis
            lux.Vis object that represents a visualization
        ldf : lux.luxDataFrame.LuxDataFrame
            LuxDataFrame with specified intent.

        Returns
        -------
        None
        '''
        import numpy as np
        import pandas as pd
        import time

        x_attr = view.get_attr_by_channel("x")[0]
        y_attr = view.get_attr_by_channel("y")[0]
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
        #checks if color is specified in the Vis
        if len(view.get_attr_by_channel("color")) == 1:
            color_attr = view.get_attr_by_channel("color")[0]
            color_attr_vals = view.data.unique_values[color_attr.attribute]
            color_cardinality = len(color_attr_vals)
            #NOTE: might want to have a check somewhere to not use categorical variables with greater than some number of categories as a Color variable----------------
            has_color = True
        else:
            color_cardinality = 1
        all_attr_vals = view.data.unique_values[groupby_attr.attribute]
        if (measure_attr!=""):
            if (measure_attr.attribute=="Record"):
                view.data = view.data.reset_index()
                #if color is specified, need to group by groupby_attr and color_attr
                if has_color:
                    view.data = view.data.groupby([groupby_attr.attribute, color_attr.attribute]).count().reset_index()
                    view.data = view.data.rename(columns={"index":"Record"})
                    view.data = view.data[[groupby_attr.attribute,color_attr.attribute,"Record"]]
                else:
                    view.data = view.data.groupby(groupby_attr.attribute).count().reset_index()
                    view.data = view.data.rename(columns={"index":"Record"})
                    view.data = view.data[[groupby_attr.attribute,"Record"]]
            else:
                #if color is specified, need to group by groupby_attr and color_attr
                if has_color:
                    groupby_result = view.data.groupby([groupby_attr.attribute, color_attr.attribute])
                else:
                    groupby_result = view.data.groupby(groupby_attr.attribute)
                view.data = groupby_result.agg(agg_func).reset_index()
            result_vals = list(view.data[groupby_attr.attribute])
            #create existing group by attribute combinations if color is specified
            #this is needed to check what combinations of group_by_attr and color_attr values have a non-zero number of elements in them
            if has_color:
                res_color_combi_vals = []
                result_color_vals = list(view.data[color_attr.attribute])
                for i in range(0, len(result_vals)):
                    res_color_combi_vals.append([result_vals[i], result_color_vals[i]])
            if (len(result_vals) != len(all_attr_vals)*color_cardinality and (isFiltered or has_color)):
                ####### ORIGINAL
                # For filtered aggregation that have missing groupby-attribute values, set these aggregated value as 0, since no datapoints
                # for vals in all_attr_vals:
                #     if (vals not in result_vals):
                #         view.data.loc[len(view.data)] = [vals]+[0]*(len(view.data.columns)-1)



                ####### SOLUTION 1 - INCOMPLETE SOLUTION, FAILS ON NONETYPE
                # start = time.time()
                # list_diff = np.setdiff1d(all_attr_vals, result_vals)
                # print(time.time() - start, 's')
                # df = pd.DataFrame({view.data.columns[1]: list_diff})

                # for col in view.data.columns[1:]:
                #     df[col] = 0

                # view.data = view.data.append(df)



                ####### SOLUTION 2
                # columns = view.data.columns

                # df = pd.DataFrame({columns[0]: all_attr_vals})
                # for col in columns[1:]:
                #     df[col] = 0
                
                # view.data = view.data.merge(df, on=columns[0], how='right', suffixes=['_left', '_right'])

                # for col in columns[1:]:
                #     view.data[col + '_left'] = view.data[col + '_left'].fillna(0)
                #     view.data[col + '_right'] = view.data[col + '_right'].fillna(0)

                #     view.data[col] = view.data[col + '_left'] + view.data[col + '_right']

                #     del view.data[col + '_left']
                #     del view.data[col + '_right']



                ####### SOLUTION 3
                # columns = view.data.columns

                # df = pd.DataFrame({columns[0]: all_attr_vals})
                # for col in columns[1:]:
                #     df[col] = 0
                
                # view.data = view.data.merge(df, on=columns[0], how='right', suffixes=['', '_right'])

                # for col in columns[1:]:
                #     view.data[col] = view.data[col].fillna(0)
                #     del view.data[col + '_right']

                
                ####### SOLUTION 4
                columns = view.data.columns
                if has_color:
                    df = pd.DataFrame({columns[0]: all_attr_vals*color_cardinality, columns[1]: pd.Series(color_attr_vals).repeat(len(all_attr_vals))})
                    view.data = view.data.merge(df, on=[columns[0],columns[1]], how='right', suffixes=['', '_right'])
                    for col in columns[2:]:
                        view.data[col] = view.data[col].fillna(0)
                    assert len(list(view.data[groupby_attr.attribute])) == len(all_attr_vals)*len(color_attr_vals), f"Aggregated data missing values compared to original range of values of `{groupby_attr.attribute, color_attr.attribute}`."
                    # for vals in all_attr_vals:
                    #     for cvals in color_attr_vals:
                    #         temp_combi = [vals, cvals]
                    #         if (temp_combi not in res_color_combi_vals):
                    #             view.data.loc[len(view.data)] = [vals]+[cvals]+[0]*(len(view.data.columns)-2)
                else:
                    df = pd.DataFrame({columns[0]: all_attr_vals})
                    
                    view.data = view.data.merge(df, on=columns[0], how='right', suffixes=['', '_right'])

                    for col in columns[1:]:
                        view.data[col] = view.data[col].fillna(0)
                    assert len(list(view.data[groupby_attr.attribute])) == len(all_attr_vals), f"Aggregated data missing values compared to original range of values of `{groupby_attr.attribute}`."
            view.data = view.data.sort_values(by=groupby_attr.attribute, ascending=True)
            view.data = view.data.reset_index()
            view.data = view.data.drop(columns="index")

    @staticmethod
    def execute_binning(view: Vis):
        '''
        Binning of data points for generating histograms

        Parameters
        ----------
        view: lux.Vis
            lux.Vis object that represents a visualization
        ldf : lux.luxDataFrame.LuxDataFrame
            LuxDataFrame with specified intent.

        Returns
        -------
        None
        '''
        import numpy as np
        import pandas as pd # is this import going to be conflicting with LuxDf?
        bin_attribute = list(filter(lambda x: x.bin_size!=0,view._inferred_intent))[0]
        #TODO:binning runs for name attribte. Name attribute has datatype quantitative which is wrong.
        counts,bin_edges = np.histogram(view.data[bin_attribute.attribute],bins=bin_attribute.bin_size)
        #bin_edges of size N+1, so need to compute bin_center as the bin location
        bin_center = np.mean(np.vstack([bin_edges[0:-1],bin_edges[1:]]), axis=0)
        # TODO: Should view.data be a LuxDataFrame or a Pandas DataFrame?
        view.data = pd.DataFrame(np.array([bin_center,counts]).T,columns=[bin_attribute.attribute, "Number of Records"])
        
    @staticmethod
    def execute_filter(view: Vis):
        assert view.data is not None, "execute_filter assumes input view.data is populated (if not, populate with LuxDataFrame values)"
        filters = utils.get_filter_specs(view._inferred_intent)
        
        if (filters):
            # TODO: Need to handle OR logic
            for filter in filters:
                view.data = PandasExecutor.apply_filter(view.data, filter.attribute, filter.filter_op, filter.value)
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