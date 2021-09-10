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
from lux.core.series import LuxSeries
from lux.vis.Clause import Clause
from lux.vis.Vis import Vis
from lux.vis.VisList import VisList
from lux.history.history import History
from lux.utils.date_utils import is_datetime_series
from lux.utils.message import Message
from lux.utils.utils import check_import_lux_widget
from typing import Dict, Union, List, Callable

# from lux.executor.Executor import *
import warnings
import traceback
import lux


class LuxDataFrame(pd.DataFrame):
    """
    A subclass of pd.DataFrame that supports all dataframe operations while housing other variables and functions for generating visual recommendations.
    """

    # MUST register here for new properties!!
    _metadata = [
        "_intent",
        "_inferred_intent",
        "_data_type",
        "unique_values",
        "cardinality",
        "_rec_info",
        "_min_max",
        "_current_vis",
        "_widget",
        "_recommendation",
        "_prev",
        "_history",
        "_saved_export",
        "_sampled",
        "_toggle_pandas_display",
        "_message",
        "_pandas_only",
        "pre_aggregated",
        "_type_override",
    ]

    def __init__(self, *args, **kw):
        self._history = History()
        self._intent = []
        self._inferred_intent = []
        self._recommendation = {}
        self._saved_export = None
        self._current_vis = []
        self._prev = None
        self._widget = None
        super(LuxDataFrame, self).__init__(*args, **kw)

        self.table_name = ""
        if lux.config.SQLconnection == "":
            from lux.executor.PandasExecutor import PandasExecutor

            lux.config.executor = PandasExecutor()
        else:
            from lux.executor.SQLExecutor import SQLExecutor

            # lux.config.executor = SQLExecutor()

        self._sampled = None
        self._approx_sample = None
        self._toggle_pandas_display = True
        self._message = Message()
        self._pandas_only = False
        # Metadata
        self._data_type = {}
        self.unique_values = None
        self.cardinality = None
        self._min_max = None
        self.pre_aggregated = None
        self._type_override = {}
        warnings.formatwarning = lux.warning_format

    @property
    def _constructor(self):
        return LuxDataFrame

    @property
    def _constructor_sliced(self):
        def f(*args, **kwargs):
            s = LuxSeries(*args, **kwargs)
            for attr in self._metadata:  # propagate metadata
                s.__dict__[attr] = getattr(self, attr, None)
            return s

        return f

    @property
    def history(self):
        return self._history

    @property
    def data_type(self):
        if not self._data_type:
            self.maintain_metadata()
        return self._data_type

    def compute_metadata(self) -> None:
        """
        Compute dataset metadata and statistics
        """
        if len(self) > 0:
            if lux.config.executor.name != "SQLExecutor":
                lux.config.executor.compute_stats(self)
            lux.config.executor.compute_dataset_metadata(self)
            self._infer_structure()
            self._metadata_fresh = True

    def maintain_metadata(self):
        """
        Maintain dataset metadata and statistics (Compute only if needed)
        """
        is_sql_tbl = lux.config.executor.name != "PandasExecutor"

        if lux.config.SQLconnection != "" and is_sql_tbl:
            from lux.executor.SQLExecutor import SQLExecutor

            # lux.config.executor = SQLExecutor()

        # Check that metadata has not yet been computed
        if lux.config.lazy_maintain:
            # Check that metadata has not yet been computed
            if not hasattr(self, "_metadata_fresh") or not self._metadata_fresh:
                # only compute metadata information if the dataframe is non-empty
                self.compute_metadata()
        else:
            self.compute_metadata()

    def expire_recs(self) -> None:
        """
        Expires and resets all recommendations
        """
        if lux.config.lazy_maintain:
            self._recs_fresh = False
            self._recommendation = {}
            self._widget = None
            self._rec_info = None
            self._sampled = None

    def expire_metadata(self) -> None:
        """
        Expire all saved metadata to trigger a recomputation the next time the data is required.
        """
        if lux.config.lazy_maintain:
            self._metadata_fresh = False
            self._data_type = None
            self.unique_values = None
            self.cardinality = None
            self._min_max = None
            self.pre_aggregated = None

    #####################
    ## Override Pandas ##
    #####################
    def __getattr__(self, name):
        ret_value = super(LuxDataFrame, self).__getattr__(name)
        self.expire_metadata()
        self.expire_recs()
        return ret_value

    def _set_axis(self, axis, labels):
        super(LuxDataFrame, self)._set_axis(axis, labels)
        self.expire_metadata()
        self.expire_recs()

    def _update_inplace(self, *args, **kwargs):
        super(LuxDataFrame, self)._update_inplace(*args, **kwargs)
        self.expire_metadata()
        self.expire_recs()

    def _set_item(self, key, value):
        super(LuxDataFrame, self)._set_item(key, value)
        self.expire_metadata()
        self.expire_recs()

    def _infer_structure(self):
        # If the dataframe is very small and the index column is not a range index, then it is likely that this is an aggregated data
        is_multi_index_flag = self.index.nlevels != 1
        not_int_index_flag = not pd.api.types.is_integer_dtype(self.index)

        is_sql_tbl = lux.config.executor.name != "PandasExecutor"

        small_df_flag = len(self) < 100 and is_sql_tbl
        if self.pre_aggregated == None:
            self.pre_aggregated = (is_multi_index_flag or not_int_index_flag) and small_df_flag
            if "Number of Records" in self.columns:
                self.pre_aggregated = True
            self.pre_aggregated = "groupby" in [event.name for event in self.history] and not is_sql_tbl

    @property
    def intent(self):
        """
        Main function to set the intent of the dataframe.
        The intent input goes through the parser, so that the string inputs are parsed into a lux.Clause object.

        Parameters
        ----------
        intent : List[str,Clause]
                intent list, can be a mix of string shorthand or a lux.Clause object

        Notes
        -----
                :doc:`../guide/intent`
        """
        return self._intent

    @intent.setter
    def intent(self, intent_input: Union[List[Union[str, Clause]], Vis]):
        is_list_input = isinstance(intent_input, list)
        is_vis_input = isinstance(intent_input, Vis)
        if not (is_list_input or is_vis_input):
            raise TypeError(
                "Input intent must be either a list (of strings or lux.Clause) or a lux.Vis object."
                "\nSee more at: https://lux-api.readthedocs.io/en/latest/source/guide/intent.html"
            )
        if is_list_input:
            self.set_intent(intent_input)
        elif is_vis_input:
            self.set_intent_as_vis(intent_input)

    def clear_intent(self):
        self.intent = []
        self.expire_recs()

    def set_intent(self, intent: List[Union[str, Clause]]):
        self.expire_recs()
        self._intent = intent
        self._parse_validate_compile_intent()

    def _parse_validate_compile_intent(self):
        self.maintain_metadata()
        from lux.processor.Parser import Parser
        from lux.processor.Validator import Validator

        self._intent = Parser.parse(self._intent)
        Validator.validate_intent(self._intent, self)
        self.maintain_metadata()
        from lux.processor.Compiler import Compiler

        self.current_vis = Compiler.compile_intent(self, self._intent)

    def copy_intent(self):
        # creates a true copy of the dataframe's intent
        output = []
        for clause in self._intent:
            temp_clause = clause.copy_clause()
            output.append(temp_clause)
        return output

    def set_intent_as_vis(self, vis: Vis):
        """
        Set intent of the dataframe based on the intent of a Vis

        Parameters
        ----------
        vis : Vis
            Input Vis object
        """
        self.expire_recs()
        self._intent = vis._inferred_intent
        self._parse_validate_compile_intent()

    def set_data_type(self, types: dict):
        """
        Set the data type for a particular attribute in the dataframe
        overriding the automatically-detected type inferred by Lux

        Parameters
        ----------
        types: dict
            Dictionary that maps attribute/column name to a specified Lux Type.
            Possible options: "nominal", "quantitative", "id", and "temporal".

        Example
        ----------
        df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/absenteeism.csv")
        df.set_data_type({"ID":"id",
                          "Reason for absence":"nominal"})
        """
        if self._type_override == None:
            self._type_override = types
        else:
            self._type_override = {**self._type_override, **types}

        if not self.data_type:
            self.maintain_metadata()

        for attr in types:
            if types[attr] not in ["nominal", "quantitative", "id", "temporal"]:
                raise ValueError(
                    f'Invalid data type option specified for {attr}. Please use one of the following supported types: ["nominal", "quantitative", "id", "temporal"]'
                )
            self.data_type[attr] = types[attr]

        self.expire_recs()

    def to_pandas(self):
        import lux.core

        return lux.core.originalDF(self, copy=False)

    @property
    def recommendation(self):
        if self._recommendation is not None and self._recommendation == {}:
            from lux.processor.Compiler import Compiler

            self.maintain_metadata()
            self.current_vis = Compiler.compile_intent(self, self._intent)
            self.maintain_recs()
        return self._recommendation

    @recommendation.setter
    def recommendation(self, recommendation: Dict):
        self._recommendation = recommendation

    @property
    def current_vis(self):
        from lux.processor.Validator import Validator

        # _parse_validate_compile_intent does not call executor,
        # we only attach data to current vis when user request current_vis
        valid_current_vis = (
            self._current_vis is not None
            and len(self._current_vis) > 0
            and self._current_vis[0].data is None
            and self._current_vis[0].intent
        )
        if valid_current_vis and Validator.validate_intent(self._current_vis[0].intent, self):
            lux.config.executor.execute(self._current_vis, self)
        return self._current_vis

    @current_vis.setter
    def current_vis(self, current_vis: Dict):
        self._current_vis = current_vis

    def _append_rec(self, rec_infolist, recommendations: Dict):
        if recommendations["collection"] is not None and len(recommendations["collection"]) > 0:
            rec_infolist.append(recommendations)

    def show_all_column_vis(self):
        if len(self.columns) > 1 and len(self.columns) < 4 and self.intent == [] or self.intent is None:
            vis = Vis(list(self.columns), self)
            if vis.mark != "":
                vis._all_column = True
                self.current_vis = VisList([vis])

    def maintain_recs(self, is_series="DataFrame"):
        # `rec_df` is the dataframe to generate the recommendations on
        # check to see if globally defined actions have been registered/removed
        if lux.config.update_actions["flag"] == True:
            self._recs_fresh = False
        show_prev = False  # flag indicating whether rec_df is showing previous df or current self

        if self._prev is not None:
            rec_df = self._prev
            rec_df._message = Message()
            rec_df.maintain_metadata()  # the prev dataframe may not have been printed before
            last_event = self.history._events[-1].name
            rec_df._message.add(
                f"Lux is visualizing the previous version of the dataframe before you applied <code>{last_event}</code>."
            )
            show_prev = True
        else:
            rec_df = self
            rec_df._message = Message()
        # Add warning message if there exist ID fields
        if len(rec_df) == 0:
            rec_df._message.add(f"Lux cannot operate on an empty {is_series}.")
        elif len(rec_df) < 5 and not rec_df.pre_aggregated:
            rec_df._message.add(
                f"The {is_series} is too small to visualize. To generate visualizations in Lux, the {is_series} must contain at least 5 rows."
            )
        elif self.index.nlevels >= 2 or self.columns.nlevels >= 2:
            rec_df._message.add(
                f"Lux does not currently support visualizations in a {is_series} "
                f"with hierarchical indexes.\n"
                f"Please convert the {is_series} into a flat "
                f"table via pandas.DataFrame.reset_index."
            )
        else:
            id_fields_str = ""
            inverted_data_type = lux.config.executor.invert_data_type(rec_df.data_type)
            if len(inverted_data_type["id"]) > 0:
                for id_field in inverted_data_type["id"]:
                    id_fields_str += f"<code>{id_field}</code>, "
                id_fields_str = id_fields_str[:-2]
                rec_df._message.add(f"{id_fields_str} is not visualized since it resembles an ID field.")

        rec_df._prev = None  # reset _prev

        # If lazy, check that recs has not yet been computed
        lazy_but_not_computed = lux.config.lazy_maintain and (
            not hasattr(rec_df, "_recs_fresh") or not rec_df._recs_fresh
        )
        eager = not lux.config.lazy_maintain

        # Check that recs has not yet been computed
        if lazy_but_not_computed or eager:
            is_sql_tbl = lux.config.executor.name == "SQLExecutor"
            rec_infolist = []
            from lux.action.row_group import row_group
            from lux.action.column_group import column_group

            # TODO: Rewrite these as register action inside default actions
            if rec_df.pre_aggregated:
                if rec_df.columns.name is not None:
                    rec_df._append_rec(rec_infolist, row_group(rec_df))
                rec_df._append_rec(rec_infolist, column_group(rec_df))
            elif not (len(rec_df) < 5 and not rec_df.pre_aggregated and not is_sql_tbl) and not (
                self.index.nlevels >= 2 or self.columns.nlevels >= 2
            ):
                from lux.action.custom import custom_actions

                # generate vis from globally registered actions and append to dataframe
                custom_action_collection = custom_actions(rec_df)
                for rec in custom_action_collection:
                    rec_df._append_rec(rec_infolist, rec)
                lux.config.update_actions["flag"] = False

            # Store _rec_info into a more user-friendly dictionary form
            rec_df._recommendation = {}
            for rec_info in rec_infolist:
                action_type = rec_info["action"]
                vlist = rec_info["collection"]
                if len(vlist) > 0:
                    rec_df._recommendation[action_type] = vlist
            rec_df._rec_info = rec_infolist
            rec_df.show_all_column_vis()
            if lux.config.render_widget:
                self._widget = rec_df.render_widget()
        # re-render widget for the current dataframe if previous rec is not recomputed
        elif show_prev:
            rec_df.show_all_column_vis()
            if lux.config.render_widget:
                self._widget = rec_df.render_widget()
        self._recs_fresh = True

    #######################################################
    ############## LuxWidget Result Display ###############
    #######################################################
    @property
    def widget(self):
        if self._widget:
            return self._widget

    @property
    def exported(self) -> Union[Dict[str, VisList], VisList]:
        """
        Get selected visualizations as exported Vis List

        Notes
        -----
        Convert the _selectedVisIdxs dictionary into a programmable VisList
        Example _selectedVisIdxs :

            {'Correlation': [0, 2], 'Occurrence': [1]}

        indicating the 0th and 2nd vis from the `Correlation` tab is selected, and the 1st vis from the `Occurrence` tab is selected.

        Returns
        -------
        Union[Dict[str,VisList], VisList]
                When there are no exported vis, return empty list -> []
                When all the exported vis is from the same tab, return a VisList of selected visualizations. -> VisList(v1, v2...)
                When the exported vis is from the different tabs, return a dictionary with the action name as key and selected visualizations in the VisList. -> {"Enhance": VisList(v1, v2...), "Filter": VisList(v5, v7...), ..}
        """
        if self.widget is None:
            warnings.warn(
                "\nNo widget attached to the dataframe."
                "Please assign dataframe to an output variable.\n"
                "See more: https://lux-api.readthedocs.io/en/latest/source/guide/FAQ.html#troubleshooting-tips",
                stacklevel=2,
            )
            return []
        exported_vis_lst = self._widget._selectedVisIdxs
        exported_vis = []
        if exported_vis_lst == {}:
            if self._saved_export:
                return self._saved_export
            warnings.warn(
                "\nNo visualization selected to export.\n"
                "See more: https://lux-api.readthedocs.io/en/latest/source/guide/FAQ.html#troubleshooting-tips",
                stacklevel=2,
            )
            return []
        if len(exported_vis_lst) == 1 and "currentVis" in exported_vis_lst:
            return self.current_vis
        elif len(exported_vis_lst) > 1:
            exported_vis = {}
            if "currentVis" in exported_vis_lst:
                exported_vis["Current Vis"] = self.current_vis
            for export_action in exported_vis_lst:
                if export_action != "currentVis":
                    exported_vis[export_action] = VisList(
                        list(
                            map(
                                self._recommendation[export_action].__getitem__,
                                exported_vis_lst[export_action],
                            )
                        )
                    )
            return exported_vis
        elif len(exported_vis_lst) == 1 and ("currentVis" not in exported_vis_lst):
            export_action = list(exported_vis_lst.keys())[0]
            exported_vis = VisList(
                list(
                    map(
                        self._recommendation[export_action].__getitem__,
                        exported_vis_lst[export_action],
                    )
                )
            )
            self._saved_export = exported_vis
            return exported_vis
        else:
            warnings.warn(
                "\nNo visualization selected to export.\n"
                "See more: https://lux-api.readthedocs.io/en/latest/source/guide/FAQ.html#troubleshooting-tips",
                stacklevel=2,
            )
            return []

    def remove_deleted_recs(self, change):
        for action in self._widget.deletedIndices:
            deletedSoFar = 0
            for index in self._widget.deletedIndices[action]:
                self._recommendation[action].remove_index(index - deletedSoFar)
                deletedSoFar += 1

    def set_intent_on_click(self, change):
        from IPython.display import display, clear_output
        from lux.processor.Compiler import Compiler

        intent_action = list(self._widget.selectedIntentIndex.keys())[0]
        vis = self._recommendation[intent_action][self._widget.selectedIntentIndex[intent_action][0]]
        self.set_intent_as_vis(vis)

        self.maintain_metadata()
        self.current_vis = Compiler.compile_intent(self, self._intent)
        self.maintain_recs()

        with self.output:
            clear_output()
            display(self._widget)

        self._widget.observe(self.remove_deleted_recs, names="deletedIndices")
        self._widget.observe(self.set_intent_on_click, names="selectedIntentIndex")

    def _ipython_display_(self):
        from IPython.display import display
        from IPython.display import clear_output
        import ipywidgets as widgets

        try:
            if self._pandas_only:
                display(self.display_pandas())
                self._pandas_only = False
            else:
                if not self.index.nlevels >= 2 or self.columns.nlevels >= 2:
                    self.maintain_metadata()

                    if self._intent != [] and (not hasattr(self, "_compiled") or not self._compiled):
                        from lux.processor.Compiler import Compiler

                        self.current_vis = Compiler.compile_intent(self, self._intent)

                if lux.config.default_display == "lux":
                    self._toggle_pandas_display = False
                else:
                    self._toggle_pandas_display = True

                # df_to_display.maintain_recs() # compute the recommendations (TODO: This can be rendered in another thread in the background to populate self._widget)
                self.maintain_recs()

                # Observers(callback_function, listen_to_this_variable)
                self._widget.observe(self.remove_deleted_recs, names="deletedIndices")
                self._widget.observe(self.set_intent_on_click, names="selectedIntentIndex")

                button = widgets.Button(
                    description="Toggle Pandas/Lux",
                    layout=widgets.Layout(width="140px", top="5px"),
                )
                self.output = widgets.Output()
                display(button, self.output)

                def on_button_clicked(b):
                    with self.output:
                        if b:
                            self._toggle_pandas_display = not self._toggle_pandas_display
                        clear_output()
                        if self._toggle_pandas_display:
                            display(self.display_pandas())
                        else:
                            # b.layout.display = "none"
                            display(self._widget)
                            # b.layout.display = "inline-block"

                button.on_click(on_button_clicked)
                on_button_clicked(None)

        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            if lux.config.pandas_fallback:
                warnings.warn(
                    "\nUnexpected error in rendering Lux widget and recommendations. "
                    "Falling back to Pandas display.\n"
                    "Please report the following issue on Github: https://github.com/lux-org/lux/issues \n",
                    stacklevel=2,
                )
                warnings.warn(traceback.format_exc())
                display(self.display_pandas())
            else:
                raise

    def display_pandas(self):
        return self.to_pandas()

    def render_widget(self, renderer: str = "altair", input_current_vis=""):
        """
        Generate a LuxWidget based on the LuxDataFrame

        Structure of widgetJSON:

        {

            'current_vis': {},
            'recommendation': [

                {

                    'action': 'Correlation',
                    'description': "some description",
                    'vspec': [

                            {Vega-Lite spec for vis 1},
                            {Vega-Lite spec for vis 2},
                            ...

                    ]

                },
                ... repeat for other actions

            ]

        }

        Parameters
        ----------
        renderer : str, optional
                Choice of visualization rendering library, by default "altair"
        input_current_vis : lux.LuxDataFrame, optional
                User-specified current vis to override default Current Vis, by default

        """
        check_import_lux_widget()
        import luxwidget

        widgetJSON = self.to_JSON(self._rec_info, input_current_vis=input_current_vis)
        return luxwidget.LuxWidget(
            currentVis=widgetJSON["current_vis"],
            recommendations=widgetJSON["recommendation"],
            intent=LuxDataFrame.intent_to_string(self._intent),
            message=self._message.to_html(),
            config={"plottingScale": lux.config.plotting_scale},
        )

    @staticmethod
    def intent_to_JSON(intent):
        from lux.utils import utils

        filter_specs = utils.get_filter_specs(intent)
        attrs_specs = utils.get_attrs_specs(intent)

        intent = {}
        intent["attributes"] = [clause.attribute for clause in attrs_specs]
        intent["filters"] = [clause.attribute for clause in filter_specs]
        return intent

    @staticmethod
    def intent_to_string(intent):
        if intent:
            return ", ".join([clause.to_string() for clause in intent])
        else:
            return ""

    def to_JSON(self, rec_infolist, input_current_vis=""):
        widget_spec = {}
        if self.current_vis:
            lux.config.executor.execute(self.current_vis, self)
            widget_spec["current_vis"] = LuxDataFrame.current_vis_to_JSON(
                self.current_vis, input_current_vis
            )
        else:
            widget_spec["current_vis"] = {}
        widget_spec["recommendation"] = []

        # Recommended Collection
        recCollection = LuxDataFrame.rec_to_JSON(rec_infolist)
        widget_spec["recommendation"].extend(recCollection)
        return widget_spec

    @staticmethod
    def current_vis_to_JSON(vlist, input_current_vis=""):
        current_vis_spec = {}
        numVC = len(vlist)  # number of visualizations in the vis list
        if numVC == 1:
            current_vis_spec = vlist[0].to_code(language=lux.config.plotting_backend, prettyOutput=False)
        elif numVC > 1:
            pass
        if vlist[0]._all_column:
            current_vis_spec["allcols"] = True
        else:
            current_vis_spec["allcols"] = False
        return current_vis_spec

    @staticmethod
    def rec_to_JSON(recs):
        rec_lst = []
        import copy

        rec_copy = copy.deepcopy(recs)
        for idx, rec in enumerate(rec_copy):
            if len(rec["collection"]) > 0:
                rec["vspec"] = []
                for vis in rec["collection"]:
                    chart = vis.to_code(language=lux.config.plotting_backend, prettyOutput=False)
                    rec["vspec"].append(chart)
                rec_lst.append(rec)
                # delete since not JSON serializable
                del rec_lst[idx]["collection"]
        return rec_lst

    def save_as_html(self, filename: str = "export.html", output=False):
        """
        Save dataframe widget as static HTML file

        Parameters
        ----------
        filename : str
            Filename for the output HTML file
        """

        if self.widget is None:
            self.maintain_metadata()
            self.maintain_recs()

        from ipywidgets.embed import embed_data

        data = embed_data(views=[self.widget])

        import json

        manager_state = json.dumps(data["manager_state"])
        widget_view = json.dumps(data["view_specs"][0])

        # Separate out header since CSS file conflict with {} notation in Python format strings
        header = """
        <head>

            <title>Lux Widget</title>
            <link rel="lux" type="image/png" sizes="96x96" href="https://github.com/lux-org/lux-resources/blob/master/logo/favicon-96x96.png?raw=True">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">
            <!-- Load RequireJS, used by the IPywidgets for dependency management -->
            <script 
            src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js" 
            integrity="sha256-Ae2Vz/4ePdIu6ZyI/5ZGsYnb+m0JlOmKPjt6XZ9JJkA=" 
            crossorigin="anonymous">
            </script>

            <!-- Load IPywidgets bundle for embedding. -->
            <script
                data-jupyter-widgets-cdn="https://unpkg.com/"
                data-jupyter-widgets-cdn-only
                src="https://cdn.jsdelivr.net/npm/@jupyter-widgets/html-manager@*/dist/embed-amd.js" 
                crossorigin="anonymous">
            </script>
            
            <style type="text/css">
                #intentBtn, #warnBtn, #exportBtn{
                display: none;
                }
                #deleteBtn {
                right: 10px !important; 
                }
                #footer-description{
                margin: 10px;
                text-align: right;
                }
            </style>
        </head>
        """
        html_template = """
        <html>
        {header}
        <body>
            
            <script type="application/vnd.jupyter.widget-state+json">
            {manager_state}
            </script>

            <script type="application/vnd.jupyter.widget-view+json">
                {widget_view}
            </script>
            
            <div id="footer-description">
            These visualizations were generated by <a href="https://github.com/lux-org/lux/" target="_blank" rel="noopener noreferrer"><img src="https://raw.githubusercontent.com/lux-org/lux-resources/master/logo/logo.png" width="65px" style="vertical-align: middle;"></img></a>
            </div>

        </body>
        </html>
        """

        manager_state = json.dumps(data["manager_state"])
        widget_view = json.dumps(data["view_specs"][0])
        rendered_template = html_template.format(
            header=header, manager_state=manager_state, widget_view=widget_view
        )
        if output:
            return rendered_template
        else:
            with open(filename, "w") as fp:
                fp.write(rendered_template)
                print(f"Saved HTML to {filename}")

    # Overridden Pandas Functions
    def head(self, n: int = 5):
        ret_val = super(LuxDataFrame, self).head(n)
        ret_val._prev = self
        ret_val._history.append_event("head", n=5)
        return ret_val

    def tail(self, n: int = 5):
        ret_val = super(LuxDataFrame, self).tail(n)
        ret_val._prev = self
        ret_val._history.append_event("tail", n=5)
        return ret_val

    def groupby(self, *args, **kwargs):
        history_flag = False
        if "history" not in kwargs or ("history" in kwargs and kwargs["history"]):
            history_flag = True
        if "history" in kwargs:
            del kwargs["history"]
        groupby_obj = super(LuxDataFrame, self).groupby(*args, **kwargs)
        for attr in self._metadata:
            groupby_obj.__dict__[attr] = getattr(self, attr, None)
        if history_flag:
            groupby_obj._history = groupby_obj._history.copy()
            groupby_obj._history.append_event("groupby", *args, **kwargs)
        groupby_obj.pre_aggregated = True
        return groupby_obj
