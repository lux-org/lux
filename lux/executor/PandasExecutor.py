#  Copyright 2019-2020 The Lux Authors.
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import pandas as pd
from lux.vis.VisList import VisList
from lux.vis.Vis import Vis
from lux.core.frame import LuxDataFrame
from lux.executor.Executor import Executor
from lux.utils import utils
from lux.utils.date_utils import is_datetime_series
from lux.utils.utils import check_import_lux_widget, check_if_id_like
from lux.utils.date_utils import is_datetime_series
import warnings


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
            # General Sampling
            if len(vis.data) > 10000:
                if (filter_executed):
                    vis._vis_data = vis.data.sample(frac=0.75 , random_state = 1)
                else:
                    if (ldf._sampled is None): # memoize unfiltered sample df 
                        ldf._sampled = vis.data.sample(frac=0.75 , random_state = 1)
                    vis._vis_data = ldf._sampled
            # TODO: Add some type of cap size on Nrows ?
            vis._vis_data = vis.data[list(attributes)]
            if (vis.mark =="bar" or vis.mark =="line"):
                PandasExecutor.execute_aggregate(vis,isFiltered = filter_executed)
            elif (vis.mark =="histogram"):
                PandasExecutor.execute_binning(vis)
            elif (vis.mark =="scatter"):
                if (len(vis.data)>10000):
                    vis._mark = "heatmap"
                    PandasExecutor.execute_2D_binning(vis)


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
    def apply_filter(df: pd.DataFrame, attribute:str, op: str, val: object) -> pd.DataFrame:
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
    @staticmethod
    def execute_2D_binning(vis: Vis):
        pd.reset_option('mode.chained_assignment')
        with pd.option_context('mode.chained_assignment', None):
            x_attr = vis.get_attr_by_channel("x")[0]
            y_attr = vis.get_attr_by_channel("y")[0]

            vis._vis_data.loc[:,"xBin"] = pd.cut(vis._vis_data[x_attr.attribute], bins=30)
            vis._vis_data.loc[:,"yBin"] = pd.cut(vis._vis_data[y_attr.attribute], bins=30)
            groups = vis._vis_data.groupby(['xBin','yBin'])[x_attr.attribute]
            result = groups.agg("count").reset_index() # .agg in this line throws SettingWithCopyWarning 
            result = result.rename(columns={x_attr.attribute:"z"})
            result = result[result["z"]!=0]

            # convert type to facilitate weighted correlation interestingess calculation
            result.loc[:,"xBinStart"] = result["xBin"].apply(lambda x: x.left).astype('float') 
            result.loc[:,"xBinEnd"] = result["xBin"].apply(lambda x: x.right)

            result.loc[:,"yBinStart"] = result["yBin"].apply(lambda x: x.left).astype('float')
            result.loc[:,"yBinEnd"] = result["yBin"].apply(lambda x: x.right)

            vis._vis_data = result.drop(columns=["xBin","yBin"])
    #######################################################
    ############ Metadata: data type, model #############
    #######################################################
    def compute_dataset_metadata(self, ldf:LuxDataFrame):
        ldf.data_type_lookup = {}
        ldf.data_type = {}
        self.compute_data_type(ldf)
        ldf.data_model_lookup = {}
        ldf.data_model = {}
        self.compute_data_model(ldf)

    def compute_data_type(self, ldf:LuxDataFrame):
        for attr in list(ldf.columns):
            temporal_var_list = ["month", "year","day","date","time"]
            if (isinstance(attr,pd._libs.tslibs.timestamps.Timestamp)): 
                # If timestamp, make the dictionary keys the _repr_ (e.g., TimeStamp('2020-04-05 00.000')--> '2020-04-05')
                ldf.data_type_lookup[attr] = "temporal"
            # elif any(var in str(attr).lower() for var in temporal_var_list):
            elif str(attr).lower() in temporal_var_list:
                ldf.data_type_lookup[attr] = "temporal"
            elif pd.api.types.is_float_dtype(ldf.dtypes[attr]):
                ldf.data_type_lookup[attr] = "quantitative"
            elif pd.api.types.is_integer_dtype(ldf.dtypes[attr]): 
                # See if integer value is quantitative or nominal by checking if the ratio of cardinality/data size is less than 0.4 and if there are less than 10 unique values
                if (ldf.pre_aggregated):
                    if (ldf.cardinality[attr]==len(ldf)):
                        ldf.data_type_lookup[attr] = "nominal"
                if ldf.cardinality[attr]/len(ldf) < 0.4 and ldf.cardinality[attr]<30: 
                    ldf.data_type_lookup[attr] = "nominal"
                else:
                    ldf.data_type_lookup[attr] = "quantitative"
                if check_if_id_like(ldf,attr): 
                    ldf.data_type_lookup[attr] = "id"
            # Eliminate this clause because a single NaN value can cause the dtype to be object
            elif pd.api.types.is_object_dtype(ldf.dtypes[attr]):
                if check_if_id_like(ldf,attr): 
                    ldf.data_type_lookup[attr] = "id"
                else:
                    ldf.data_type_lookup[attr] = "nominal"
            elif is_datetime_series(ldf.dtypes[attr]): #check if attribute is any type of datetime dtype
                ldf.data_type_lookup[attr] = "temporal"
        # for attr in list(df.dtypes[df.dtypes=="int64"].keys()):
        #   if self.cardinality[attr]>50:
        if (ldf.index.dtype !='int64' and ldf.index.name):
            ldf.data_type_lookup[ldf.index.name] = "nominal"
        ldf.data_type = self.mapping(ldf.data_type_lookup)

        from pandas.api.types import is_datetime64_any_dtype as is_datetime
        non_datetime_attrs = []
        for attr in ldf.columns:
            if ldf.data_type_lookup[attr] == 'temporal' and not is_datetime(ldf[attr]):
                non_datetime_attrs.append(attr)
        if len(non_datetime_attrs) == 1:
            warnings.warn(
                    f"\nLux detects that the attribute '{non_datetime_attrs[0]}' may be temporal.\n" 
                    "In order to display visualizations for this attribute accurately, temporal attributes should be converted to Pandas Datetime objects.\n\n"
                    "Please consider converting this attribute using the pd.to_datetime function and providing a 'format' parameter to specify datetime format of the attribute.\n"
                    "For example, you can convert the 'month' attribute in a dataset to Datetime type via the following command:\n\n\t df['month'] = pd.to_datetime(df['month'], format='%m')\n\n"
                    "See more at: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.to_datetime.html\n"
                    ,stacklevel=2)
        elif len(non_datetime_attrs) > 1:
            warnings.warn(
                    f"\nLux detects that attributes {non_datetime_attrs} may be temporal.\n" 
                    "In order to display visualizations for these attributes accurately, temporal attributes should be converted to Pandas Datetime objects.\n\n"
                    "Please consider converting these attributes using the pd.to_datetime function and providing a 'format' parameter to specify datetime format of the attribute.\n"
                    "For example, you can convert the 'month' attribute in a dataset to Datetime type via the following command:\n\n\t df['month'] = pd.to_datetime(df['month'], format='%m')\n\n"
                    "See more at: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.to_datetime.html\n"
                    ,stacklevel=2)
    def compute_data_model(self, ldf:LuxDataFrame):
        ldf.data_model = {
            "measure": ldf.data_type["quantitative"],
            "dimension": ldf.data_type["ordinal"] + ldf.data_type["nominal"] + ldf.data_type["temporal"]  + ldf.data_type["id"]
        }
        ldf.data_model_lookup = self.reverseMapping(ldf.data_model)


    def compute_stats(self, ldf:LuxDataFrame):
        # precompute statistics
        ldf.unique_values = {}
        ldf._min_max = {}
        ldf.cardinality = {}

        for attribute in ldf.columns:
            
            if (isinstance(attribute,pd._libs.tslibs.timestamps.Timestamp)): 
                # If timestamp, make the dictionary keys the _repr_ (e.g., TimeStamp('2020-04-05 00.000')--> '2020-04-05')
                attribute_repr = str(attribute._date_repr)
            else:
                attribute_repr = attribute
            if ldf.dtypes[attribute] != "float64":# and not pd.api.types.is_datetime64_ns_dtype(self.dtypes[attribute]):
                ldf.unique_values[attribute_repr] = list(ldf[attribute].unique())
                ldf.cardinality[attribute_repr] = len(ldf.unique_values[attribute])
            else:   
                ldf.cardinality[attribute_repr] = 999 # special value for non-numeric attribute
            if ldf.dtypes[attribute] == "float64" or ldf.dtypes[attribute] == "int64":
                ldf._min_max[attribute_repr] = (ldf[attribute].min(), ldf[attribute].max())
        if (ldf.index.dtype !='int64'):
            index_column_name = ldf.index.name
            ldf.unique_values[index_column_name] = list(ldf.index)
            ldf.cardinality[index_column_name] = len(ldf.index)