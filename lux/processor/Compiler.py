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

from lux.vis import Clause
from typing import List, Dict, Union
from lux.vis.Vis import Vis
from lux.processor.Validator import Validator
from lux.core.frame import LuxDataFrame
from lux.vis.VisList import VisList
from lux.utils import date_utils
from lux.utils import utils
import pandas as pd
import numpy as np
import warnings
import copy
import lux

from IPython.core.debugger import set_trace


class Compiler:
    """
    Given a intent with underspecified inputs, compile the intent into fully specified visualizations for visualization.
    """

    # static var for count col bc used a lot
    count_col = Clause(
        attribute="Record",
        aggregation="count",
        data_model="measure",
        data_type="quantitative",
    )

    def __init__(self):
        self.name = "Compiler"
        warnings.formatwarning = lux.warning_format

    def __repr__(self):
        return f"<Compiler>"

    @staticmethod
    def compile_vis(ldf: LuxDataFrame, vis: Vis) -> Vis:
        """
        Root method for compiling visualizations

        Parameters
        ----------
        ldf : LuxDataFrame
        vis : Vis

        Returns
        -------
        Vis
            Compiled Vis object
        """
        if vis:
            # autofill data type/model information
            Compiler.populate_data_type_model(
                ldf, [vis]
            )  # DEBUG NOTE this doesnt count the record as measure if already present
            # remove invalid visualizations from collection
            Compiler.remove_all_invalid([vis])
            # autofill viz related information
            Compiler.determine_encoding(ldf, vis)
            ldf._compiled = True
            return vis

    @staticmethod
    def compile_intent(ldf: LuxDataFrame, _inferred_intent: List[Clause]) -> VisList:
        """
        Compiles input specifications in the intent of the ldf into a collection of lux.vis objects for visualization.
        1) Enumerate a collection of visualizations interested by the user to generate a vis list
        2) Expand underspecified specifications(lux.Clause) for each of the generated visualizations.
        3) Determine encoding properties for each vis

        Parameters
        ----------
        ldf : lux.core.frame
                LuxDataFrame with underspecified intent.
        vis_collection : list[lux.vis.Vis]
                empty list that will be populated with specified lux.Vis objects.

        Returns
        -------
        vis_collection: list[lux.Vis]
                vis list with compiled lux.Vis objects.
        """
        valid_intent = _inferred_intent  # ensures intent is non-empty
        if valid_intent and Validator.validate_intent(_inferred_intent, ldf, True):
            vis_collection = Compiler.enumerate_collection(_inferred_intent, ldf)
            # autofill data type/model information
            Compiler.populate_data_type_model(ldf, vis_collection)
            # remove invalid visualizations from collection
            if len(vis_collection) >= 1:
                vis_collection = Compiler.remove_all_invalid(vis_collection)
            for vis in vis_collection:
                # autofill viz related information
                Compiler.determine_encoding(ldf, vis)

            vis_collection = Compiler.enforce_mark_type(_inferred_intent, vis_collection)
            vis_collection.remove_duplicates()  # BUG this doesnt remove dups where the intent may look different but vis is the same

            ldf._compiled = True
            return vis_collection
        elif _inferred_intent:
            return []

    @staticmethod
    def enforce_mark_type(_inferred_intent: List[Clause], vis_collection: VisList) -> VisList:
        """
        Hacky way to make sure the returned vis in viscollection comply with the intent.
        The vis compiler default to another vis if unable to make the right one so migtht not all be the
        right mark.
        """

        enforce_mark = ""

        for c in _inferred_intent:
            if c.mark_type:
                enforce_mark = c.mark_type
                break

        if enforce_mark:
            vis_collection = list(filter(lambda x: x.mark == enforce_mark, vis_collection))

        return VisList(vis_collection)

    @staticmethod
    def enumerate_collection(_inferred_intent: List[Clause], ldf: LuxDataFrame) -> VisList:
        """
        Given specifications that have been expanded thorught populateOptions,
        recursively iterate over the resulting list combinations to generate a vis list.

        Parameters
        ----------
        ldf : lux.core.frame
                LuxDataFrame with underspecified intent.

        Returns
        -------
        VisList: list[lux.Vis]
                vis list with compiled lux.Vis objects.
        """
        import copy

        intent = Compiler.populate_wildcard_options(_inferred_intent, ldf)
        attributes = intent["attributes"]
        filters = intent["filters"]
        if len(attributes) == 0 and len(filters) > 0:
            return []

        collection = []

        # TODO: generate combinations of column attributes recursively by continuing to accumulate attributes for len(colAtrr) times
        def combine(col_attrs, accum):
            last = len(col_attrs) == 1
            n = len(col_attrs[0])
            for i in range(n):
                column_list = copy.deepcopy(accum + [col_attrs[0][i]])
                if last:
                    # if we have filters, generate combinations for each row.
                    if len(filters) > 0:
                        for row in filters:
                            _inferred_intent = copy.deepcopy(column_list + [row])
                            vis = Vis(_inferred_intent)
                            collection.append(vis)
                    else:
                        vis = Vis(column_list)
                        collection.append(vis)
                else:
                    combine(col_attrs[1:], column_list)

        combine(attributes, [])
        return VisList(collection)

    @staticmethod
    def populate_data_type_model(ldf, vlist):
        """
        Given a underspecified Clause, populate the data_type and data_model information accordingly

        Parameters
        ----------
        ldf : lux.core.frame
                LuxDataFrame with underspecified intent

        vis_collection : list[lux.vis.Vis]
                List of lux.Vis objects that will have their underspecified Clause details filled out.
        """
        # TODO: copy might not be neccesary
        from lux.utils.date_utils import is_datetime_string

        data_model_lookup = lux.config.executor.compute_data_model_lookup(ldf.data_type)
        for vis in vlist:
            for clause in vis._inferred_intent:
                if clause.description == "?":
                    clause.description = ""
                # TODO: Note that "and not is_datetime_string(clause.attribute))" is a temporary hack and breaks the `test_row_column_group` example
                if clause.attribute != "" and clause.attribute != "Record":
                    if clause.data_type == "":
                        clause.data_type = ldf.data_type[clause.attribute]
                    if clause.data_type == "id":
                        clause.data_type = "nominal"
                    if clause.data_type == "geographical":
                        clause.data_type = "nominal"
                    if clause.data_model == "":
                        clause.data_model = data_model_lookup[clause.attribute]
                if clause.value != "":
                    # If user provided title for Vis, then don't override.
                    if vis.title == "":
                        if isinstance(clause.value, np.datetime64):
                            chart_title = date_utils.date_formatter(clause.value, ldf)
                        else:
                            chart_title = clause.value
                        vis.title = f"{clause.attribute} {clause.filter_op} {chart_title}"
            vis._ndim = 0
            vis._nmsr = 0

            for clause in vis._inferred_intent:
                if clause.value == "":
                    if clause.data_model == "dimension":
                        vis._ndim += 1
                    elif (
                        clause.data_model == "measure" and clause.attribute != "Record"
                    ):  # NOTE Will - I think record should be counted but that breaks other stuff
                        vis._nmsr += 1

    @staticmethod
    def remove_all_invalid(vis_collection: VisList) -> VisList:
        """
        Given an expanded vis list, remove all visualizations that are invalid.
        Currently, the invalid visualizations are ones that do not contain:
        - two of the same attribute,
        - more than two temporal attributes,
        - no overlapping attributes (same filter attribute and visualized attribute),
        - more than 1 temporal attribute with 2 or more measures
        Parameters
        ----------
        vis_collection : list[lux.vis.Vis]
                empty list that will be populated with specified lux.Vis objects.
        Returns
        -------
        lux.vis.VisList
                vis list with compiled lux.Vis objects.
        """
        new_vc = []
        for vis in vis_collection:
            num_temporal_specs = 0
            attribute_set = set()
            for clause in vis._inferred_intent:
                attribute_set.add(clause.attribute)
                if clause.data_type == "temporal":
                    num_temporal_specs += 1
            all_distinct_specs = 0 == len(vis._inferred_intent) - len(attribute_set)
            if (
                num_temporal_specs < 2
                and all_distinct_specs
                and not (vis._nmsr == 2 and num_temporal_specs == 1)
                and not (vis._nmsr == 3 and vis._ndim == 1)
            ):
                new_vc.append(vis)
            # else:
            # 	warnings.warn("\nThere is more than one duplicate attribute specified in the intent.\nPlease check your intent specification again.")

        return VisList(new_vc)

    @staticmethod
    def fill_mark_encoding(mark_channel_clause: Clause, ldf: LuxDataFrame, vis: Vis):
        """
        User has specified mark type. Make sure is valid and try to fill in gaps

        BUG
        Leads to some redundancies if enumerate_collection returns different data slices that arent used

        # this returns 4 of same vis, order matters tho
        intent = [lux.Clause("Horsepower", mark_type="histogram"), lux.Clause("?", mark_type="histogram")]
        vis = VisList(intent,df)
        """

        auto_channel = {}
        if vis.mark == "histogram":
            if vis.get_attr_by_data_model("measure", exclude_record=True):
                auto_channel = Compiler.make_histogram(vis)

        elif vis.mark == "bar" or vis.mark == "line":
            if vis._ndim >= 1:
                auto_channel = Compiler.make_line_or_bar(vis, ldf)

        elif vis.mark == "scatter":
            if vis._nmsr >= 2:
                auto_channel = Compiler.make_scatter(vis)

        elif vis.mark == "heatmap":
            if vis._nmsr >= 2:  # TODO loosen this restriction
                auto_channel = Compiler.make_heatmap(vis)
                # lux.config.heatmap_bin_size # TODO change this too with ldf.cardinality[dimension.attribute]

        elif vis.mark == "boxplot":
            if mark_channel_clause.attribute and mark_channel_clause.data_type == "measure":
                auto_channel["y"] = mark_channel_clause
            elif vis.get_attr_by_data_model("measure"):
                m_clause = vis.get_attr_by_data_model("measure")[0]
                auto_channel["y"] = m_clause

        return auto_channel

    @staticmethod
    def make_histogram(vis: Vis):
        measure = vis.get_attr_by_data_model("measure", exclude_record=True)[0]
        my_count_col = None # to avoid the shared statis class object
        if not len(vis.get_attr_by_attr_name("Record")):
            my_count_col = copy.copy(Compiler.count_col)
            if hasattr(measure, "channel") and measure.channel == "x":
                my_count_col.channel = "y"
            vis._inferred_intent.append(my_count_col)
            #vis._nmsr += 1
        else:
            my_count_col = vis.get_attr_by_attr_name("Record")[0]
        # If no bin specified, then default as 10
        if measure.bin_size == 0:
            measure.bin_size = 10
        auto_channel = {"x": measure, "y": my_count_col}
        vis._mark = "histogram"

        return auto_channel

    @staticmethod
    def make_line_or_bar(vis: Vis, ldf: LuxDataFrame):
        dimensions = vis.get_attr_by_data_model("dimension")
        d1 = dimensions[0]
        d2 = None
        color_attr = None

        if len(dimensions) > 1:
            d2 = dimensions[1]

        if (vis._nmsr == 0) and not len(vis.get_attr_by_attr_name("Record")):
            my_count_col = copy.copy(Compiler.count_col)
            vis._inferred_intent.append(
                my_count_col
            )  # TODO this causes redundancy sometimes?? only add ifg record not in therrrrr
            # vis._nmsr += 1

        measure = vis.get_attr_by_data_model("measure")[0]

        if d2:  # line or bar broken down by dimension
            if ldf.cardinality[d1.attribute] < ldf.cardinality[d2.attribute]:
                # d1.channel = "color"
                vis.remove_column_from_spec(d1.attribute)
                dimension = d2
                color_attr = d1
            else:
                # if same attribute then remove_column_from_spec will remove both dims, we only want to remove one
                if d1.attribute == d2.attribute:
                    vis._inferred_intent.pop(0)
                else:
                    vis.remove_column_from_spec(d2.attribute)
                dimension = d1
                color_attr = d2

            # if not ldf.pre_aggregated: # what happens if is pre-aggregated?
        else:
            dimension = d1

        _m, auto_channel = Compiler.line_bar_geo_helper(ldf, dimension, measure)

        if not vis._mark:
            vis._mark = _m

        # if override_mark:
        #     vis._mark = override_mark

        if color_attr:
            auto_channel["color"] = color_attr

        return auto_channel

    @staticmethod
    def line_bar_geo_helper(ldf: LuxDataFrame, dimension: Clause, measure: Clause):
        dim_type = dimension.data_type
        # If no aggregation function is specified, then default as average
        if measure.aggregation == "":
            measure.set_aggregation("mean")
        if dim_type == "temporal" or dim_type == "oridinal":
            return "line", {"x": dimension, "y": measure}
        else:  # unordered categorical
            # if cardinality large than 5 then sort bars
            if ldf.cardinality[dimension.attribute] > 5:
                dimension.sort = "ascending"
            if utils.like_geo(dimension.get_attr()):
                return "geographical", {"x": dimension, "y": measure}
            return "bar", {"x": measure, "y": dimension}

    @staticmethod
    def make_scatter(vis: Vis):
        measures = vis.get_attr_by_data_model("measure")
        dims = vis.get_attr_by_data_model("dimension")

        m1 = measures[0]
        m2 = measures[1]

        m1.set_aggregation(None)  # this should set in the og vis object too by reference
        m2.set_aggregation(None)

        vis._mark = "scatter"
        auto_channel = {"x": m1, "y": m2}

        # use color if available. Prefer dimension then measure attribute
        if dims:
            vis.remove_column_from_spec(dims[0])
            auto_channel["color"] = dims[0]
        elif len(measures) > 2:
            m3 = measures[2]
            auto_channel["color"] = m3

        return auto_channel

    @staticmethod
    # TODO using the same metrics as scatter rn but can likely loosen
    def make_heatmap(vis: Vis):
        measures = vis.get_attr_by_data_model("measure")
        dims = vis.get_attr_by_data_model("dimension")

        m1 = measures[0]
        m2 = measures[1]

        m1.set_aggregation(None)  # this should set in the og vis object too by reference
        m2.set_aggregation(None)

        vis._mark = "heatmap"
        auto_channel = {"x": m1, "y": m2}

        # use color if available. Prefer dimension then measure attribute
        if dims:
            vis.remove_column_from_spec(dims[0])
            auto_channel["color"] = dims[0]
        elif len(measures) > 2:
            m3 = measures[2]
            auto_channel["color"] = m3

        return auto_channel

    @staticmethod
    def determine_encoding(ldf: LuxDataFrame, vis: Vis):
        """
        Populates Vis with the appropriate mark type and channel information based on ShowMe logic
        Currently support up to 3 dimensions or measures

        Parameters
        ----------
        ldf : lux.core.frame
                LuxDataFrame with underspecified intent
        vis : lux.vis.Vis

        Returns
        -------
        None

        Notes
        -----
        Implementing automatic encoding from Tableau's VizQL
        Mackinlay, J. D., Hanrahan, P., & Stolte, C. (2007).
        Show Me: Automatic presentation for visual analysis.
        IEEE Transactions on Visualization and Computer Graphics, 13(6), 1137–1144.
        https://doi.org/10.1109/TVCG.2007.70594
        """

        """
        vis._inferred_intent has all the intent info 

        """
        # Count number of measures and dimensions
        ndim = vis._ndim
        nmsr = vis._nmsr
        # preserve to add back to _inferred_intent later
        filters = utils.get_filter_specs(vis._inferred_intent)
        auto_channel = {}
        mark_channel_clause = None
        mark_type = ""

        # see if user has specified vis type
        for clause in vis._inferred_intent:
            if clause.mark_type:
                mark_type = clause.mark_type
                mark_channel_clause = clause

        if mark_type:
            vis._mark = mark_type
            auto_channel = Compiler.fill_mark_encoding(mark_channel_clause, ldf, vis)

        # ShowMe logic + additional heuristics
        if not auto_channel:
            if ndim == 0 and nmsr == 1:
                # Histogram
                auto_channel = Compiler.make_histogram(vis)

            elif (ndim == 1 or ndim == 2) and (nmsr == 0 or nmsr == 1):
                # Line or Bar Chart
                auto_channel = Compiler.make_line_or_bar(vis, ldf)

            elif (ndim == 0 or ndim == 1) and (nmsr == 2 or nmsr == 3):
                # Scatterplot
                auto_channel = Compiler.make_scatter(vis)

        relevant_attributes = [auto_channel[channel].attribute for channel in auto_channel]
        relevant_min_max = dict(
            (attr, ldf._min_max[attr])
            for attr in relevant_attributes
            if attr != "Record" and attr in ldf._min_max
        )
        # Replace scatterplot with heatmap
        HBIN_START = 5000
        if vis.mark == "scatter" and lux.config.heatmap and len(ldf) > HBIN_START:
            vis._postbin = True
            ldf._message.add_unique(
                f"Large scatterplots detected: Lux is automatically binning scatterplots to heatmaps.",
                priority=98,
            )
            vis._mark = "heatmap"
        vis._min_max = relevant_min_max
        if auto_channel != {}:
            vis = Compiler.enforce_specified_channel(vis, auto_channel)
            vis._inferred_intent.extend(filters)  # add back the preserved filters

    @staticmethod
    def enforce_specified_channel(vis: Vis, auto_channel: Dict[str, str]):
        """
        Enforces that the channels specified in the Vis by users overrides the showMe autoChannels.

        Parameters
        ----------
        vis : lux.vis.Vis
                Input Vis without channel specification.
        auto_channel : Dict[str,str]
                Key-value pair in the form [channel: attributeName] specifying the showMe recommended channel location.

        Returns
        -------
        vis : lux.vis.Vis
                Vis with channel specification combining both original and auto_channel specification.

        Raises
        ------
        ValueError
                Ensures no more than one attribute is placed in the same channel.
        """
        # result of enforcing specified channel will be stored in result_dict
        result_dict = {}
        # specified_dict={"x":[],"y":[list of Dobj with y specified as channel]}
        specified_dict = {}
        # create a dictionary of specified channels in the given dobj
        for val in auto_channel.keys():
            specified_dict[val] = vis.get_attr_by_channel(val)
            result_dict[val] = ""
        # for every element, replace with what's in specified_dict if specified
        for sVal, sAttr in specified_dict.items():
            if len(sAttr) == 1:  # if specified in dobj
                # remove the specified channel from auto_channel (matching by value, since channel key may not be same)
                for i in list(auto_channel.keys()):
                    # need to ensure that the channel is the same (edge case when duplicate Cols with same attribute name)
                    if (
                        auto_channel[i].attribute == sAttr[0].attribute
                        and auto_channel[i].channel == sVal
                    ):
                        auto_channel.pop(i)
                        break
                sAttr[0].channel = sVal
                result_dict[sVal] = sAttr[0]
            elif len(sAttr) > 1:
                set_trace()

                raise ValueError(
                    "There should not be more than one attribute specified in the same channel."
                )
        # For the leftover channels that are still unspecified in result_dict,
        # and the leftovers in the auto_channel specification,
        # step through them together and fill it automatically.
        leftover_channels = list(filter(lambda x: result_dict[x] == "", result_dict))
        for leftover_channel, leftover_encoding in zip(leftover_channels, auto_channel.values()):
            leftover_encoding.channel = leftover_channel
            result_dict[leftover_channel] = leftover_encoding
        vis._inferred_intent = list(result_dict.values())
        return vis

    @staticmethod
    # def populate_wildcard_options(ldf: LuxDataFrame) -> dict:
    def populate_wildcard_options(_inferred_intent: List[Clause], ldf: LuxDataFrame) -> dict:
        """
        Given wildcards and constraints in the LuxDataFrame's intent,
        return the list of available values that satisfies the data_type or data_model constraints.

        Parameters
        ----------
        ldf : LuxDataFrame
                LuxDataFrame with row or attributes populated with available wildcard options.

        Returns
        -------
        intent: Dict[str,list]
                a dictionary that holds the attributes and filters generated from wildcards and constraints.
        """
        import copy
        from lux.utils.utils import convert_to_list

        inverted_data_type = lux.config.executor.invert_data_type(ldf.data_type)
        data_model = lux.config.executor.compute_data_model(ldf.data_type)

        intent = {"attributes": [], "filters": []}
        for clause in _inferred_intent:
            spec_options = []
            if clause.value == "":  # attribute
                if clause.attribute == "?":
                    options = set(list(ldf.columns))  # all attributes
                    if clause.data_type != "":
                        options = options.intersection(set(inverted_data_type[clause.data_type]))
                    if clause.data_model != "":
                        options = options.intersection(set(data_model[clause.data_model]))
                    options = list(options)
                else:
                    options = convert_to_list(clause.attribute)
                for optStr in options:
                    if str(optStr) not in clause.exclude:
                        spec_copy = copy.copy(clause)
                        spec_copy.attribute = optStr
                        spec_options.append(spec_copy)
                intent["attributes"].append(spec_options)
            else:  # filters
                attr_lst = convert_to_list(clause.attribute)
                for attr in attr_lst:
                    options = []
                    if clause.value == "?":
                        options = ldf.unique_values[attr]
                        specInd = _inferred_intent.index(clause)
                        _inferred_intent[specInd] = Clause(
                            attribute=clause.attribute,
                            filter_op="=",
                            value=list(options),
                        )
                    else:
                        options.extend(convert_to_list(clause.value))
                    for optStr in options:
                        if str(optStr) not in clause.exclude:
                            spec_copy = copy.copy(clause)
                            spec_copy.attribute = attr
                            spec_copy.value = optStr
                            spec_options.append(spec_copy)
                intent["filters"].extend(spec_options)

        return intent
