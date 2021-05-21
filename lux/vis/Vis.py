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

from typing import List, Callable, Union
from lux.vis.Clause import Clause
from lux.utils.utils import check_import_lux_widget
import lux
import warnings


class Vis:
    """
    Vis Object represents a collection of fully fleshed out specifications required for data fetching and visualization.
    """

    def __init__(self, intent, source=None, title="", score=0.0):
        self._intent = intent  # user's original intent to Vis
        self._inferred_intent = intent  # re-written, expanded version of user's original intent
        self._source = source  # original data attached to the Vis
        self._vis_data = None  # processed data for Vis (e.g., selected, aggregated, binned)
        self._code = None
        self._mark = ""
        self._min_max = {}
        self._postbin = None
        self.title = title
        self.score = score
        self._all_column = False
        self.approx = False
        self.refresh_source(self._source)

    def __repr__(self):
        all_clause = all([isinstance(unit, lux.Clause) for unit in self._inferred_intent])
        if all_clause:
            filter_intents = None
            channels, additional_channels = [], []
            for clause in self._inferred_intent:

                if hasattr(clause, "value"):
                    if clause.value != "":
                        filter_intents = clause
                if hasattr(clause, "attribute"):
                    if clause.attribute != "":
                        if clause.aggregation != "" and clause.aggregation is not None:
                            attribute = f"{clause._aggregation_name.upper()}({clause.attribute})"
                        elif clause.bin_size > 0:
                            attribute = f"BIN({clause.attribute})"
                        else:
                            attribute = clause.attribute
                        if clause.channel == "x":
                            channels.insert(0, [clause.channel, attribute])
                        elif clause.channel == "y":
                            channels.insert(1, [clause.channel, attribute])
                        elif clause.channel != "":
                            additional_channels.append([clause.channel, attribute])

            channels.extend(additional_channels)
            str_channels = ""
            for channel in channels:
                str_channels += f"{channel[0]}: {channel[1]}, "

            if filter_intents:
                return f"<Vis  ({str_channels[:-2]} -- [{filter_intents.attribute}{filter_intents.filter_op}{filter_intents.value}]) mark: {self._mark}, score: {self.score} >"
            else:
                return f"<Vis  ({str_channels[:-2]}) mark: {self._mark}, score: {self.score} >"
        else:
            # When Vis not compiled (e.g., when self._source not populated), print original intent
            return f"<Vis  ({str(self._intent)}) mark: {self._mark}, score: {self.score} >"

    @property
    def data(self):
        return self._vis_data

    @property
    def code(self):
        return self._code

    @property
    def mark(self):
        return self._mark

    @property
    def min_max(self):
        return self._min_max

    @property
    def intent(self):
        return self._intent

    @intent.setter
    def intent(self, intent: List[Clause]) -> None:
        self.set_intent(intent)

    def set_intent(self, intent: List[Clause]) -> None:
        """
        Sets the intent of the Vis and refresh the source based on the new intent

        Parameters
        ----------
        intent : List[Clause]
                Query specifying the desired VisList
        """
        self._intent = intent
        self.refresh_source(self._source)

    def _ipython_display_(self):
        from IPython.display import display

        check_import_lux_widget()
        import luxwidget

        if self.data is None:
            raise Exception(
                "No data is populated in Vis. In order to generate data required for the vis, use the 'refresh_source' function to populate the Vis with a data source (e.g., vis.refresh_source(df))."
            )
        else:
            from lux.core.frame import LuxDataFrame

            widget = luxwidget.LuxWidget(
                currentVis=LuxDataFrame.current_vis_to_JSON([self]),
                recommendations=[],
                intent="",
                message="",
                config={"plottingScale": lux.config.plotting_scale},
            )
            display(widget)

    def get_attr_by_attr_name(self, attr_name):
        return list(filter(lambda x: x.attribute == attr_name, self._inferred_intent))

    def get_attr_by_channel(self, channel):
        spec_obj = list(
            filter(
                lambda x: x.channel == channel and x.value == "" if hasattr(x, "channel") else False,
                self._inferred_intent,
            )
        )
        return spec_obj

    def get_attr_by_data_model(self, dmodel, exclude_record=False):
        if exclude_record:
            return list(
                filter(
                    lambda x: x.data_model == dmodel and x.value == ""
                    if x.attribute != "Record" and hasattr(x, "data_model")
                    else False,
                    self._inferred_intent,
                )
            )
        else:
            return list(
                filter(
                    lambda x: x.data_model == dmodel and x.value == ""
                    if hasattr(x, "data_model")
                    else False,
                    self._inferred_intent,
                )
            )

    def get_attr_by_data_type(self, dtype):
        return list(
            filter(
                lambda x: x.data_type == dtype and x.value == "" if hasattr(x, "data_type") else False,
                self._inferred_intent,
            )
        )

    def remove_filter_from_spec(self, value):
        new_intent = list(filter(lambda x: x.value != value, self._inferred_intent))
        self.set_intent(new_intent)

    def remove_column_from_spec(self, attribute, remove_first: bool = False):
        """
        Removes an attribute from the Vis's clause

        Parameters
        ----------
        attribute : str
                attribute to be removed
        remove_first : bool, optional
                Boolean flag to determine whether to remove all instances of the attribute or only one (first) instance, by default False
        """
        if not remove_first:
            new_inferred = list(filter(lambda x: x.attribute != attribute, self._inferred_intent))
            self._inferred_intent = new_inferred
            self._intent = new_inferred
        elif remove_first:
            new_inferred = []
            skip_check = False
            for i in range(0, len(self._inferred_intent)):
                if self._inferred_intent[i].value == "":  # clause is type attribute
                    column_spec = []
                    column_names = self._inferred_intent[i].attribute
                    # if only one variable in a column, columnName results in a string and not a list so
                    # you need to differentiate the cases
                    if isinstance(column_names, list):
                        for column in column_names:
                            if (column != attribute) or skip_check:
                                column_spec.append(column)
                            elif remove_first:
                                remove_first = True
                        new_inferred.append(Clause(column_spec))
                    else:
                        if column_names != attribute or skip_check:
                            new_inferred.append(Clause(attribute=column_names))
                        elif remove_first:
                            skip_check = True
                else:
                    new_inferred.append(self._inferred_intent[i])
            self._intent = new_inferred
            self._inferred_intent = new_inferred

    def to_altair(self, standalone=False) -> str:
        """
        Generate minimal Altair code to visualize the Vis

        Parameters
        ----------
        standalone : bool, optional
                Flag to determine if outputted code uses user-defined variable names or can be run independently, by default False

        Returns
        -------
        str
                String version of the Altair code. Need to print out the string to apply formatting.
        """
        from lux.vislib.altair.AltairRenderer import AltairRenderer

        renderer = AltairRenderer(output_type="Altair")
        self._code = renderer.create_vis(self, standalone)
        return self._code

    def to_matplotlib(self) -> str:
        """
        Generate minimal Matplotlib code to visualize the Vis

        Returns
        -------
        str
                String version of the Matplotlib code. Need to print out the string to apply formatting.
        """
        from lux.vislib.matplotlib.MatplotlibRenderer import MatplotlibRenderer

        renderer = MatplotlibRenderer(output_type="matplotlib")
        self._code = renderer.create_vis(self)
        return self._code

    def _to_matplotlib_svg(self) -> str:
        """
        Private method to render Vis as SVG with Matplotlib

        Returns
        -------
        str
                String version of the SVG.
        """
        from lux.vislib.matplotlib.MatplotlibRenderer import MatplotlibRenderer

        renderer = MatplotlibRenderer(output_type="matplotlib_svg")
        self._code = renderer.create_vis(self)
        return self._code

    def to_vegalite(self, prettyOutput=True) -> Union[dict, str]:
        """
        Generate minimal Vega-Lite code to visualize the Vis

        Returns
        -------
        Union[dict,str]
                String or Dictionary of the VegaLite JSON specification
        """
        import json
        from lux.vislib.altair.AltairRenderer import AltairRenderer

        renderer = AltairRenderer(output_type="VegaLite")
        self._code = renderer.create_vis(self)
        if prettyOutput:
            return (
                "** Remove this comment -- Copy Text Below to Vega Editor(vega.github.io/editor) to visualize and edit **\n"
                + json.dumps(self._code, indent=2)
            )
        else:
            return self._code

    def to_code(self, language="vegalite", **kwargs):
        """
        Export Vis object to code specification

        Parameters
        ----------
        language : str, optional
            choice of target language to produce the visualization code in, by default "vegalite"

        Returns
        -------
        spec:
            visualization specification corresponding to the Vis object
        """
        if language == "vegalite":
            return self.to_vegalite(**kwargs)
        elif language == "altair":
            return self.to_altair(**kwargs)
        elif language == "matplotlib":
            return self.to_matplotlib()
        elif language == "matplotlib_svg":
            return self._to_matplotlib_svg()
        else:
            warnings.warn(
                "Unsupported plotting backend. Lux currently only support 'altair', 'vegalite', or 'matplotlib'",
                stacklevel=2,
            )

    def refresh_source(self, ldf):  # -> Vis:
        """
        Loading the source data into the Vis by instantiating the specification and
        populating the Vis based on the source data, effectively "materializing" the Vis.

        Parameters
        ----------
        ldf : LuxDataframe
                Input Dataframe to be attached to the Vis

        Returns
        -------
        Vis
                Complete Vis with fully-specified fields

        See Also
        --------
        lux.Vis.VisList.refresh_source

        Note
        ----
        Function derives a new _inferred_intent by instantiating the intent specification on the new data
        """
        if ldf is not None:
            from lux.processor.Parser import Parser
            from lux.processor.Validator import Validator
            from lux.processor.Compiler import Compiler

            self.check_not_vislist_intent()

            ldf.maintain_metadata()
            self._source = ldf
            self._inferred_intent = Parser.parse(self._intent)
            Validator.validate_intent(self._inferred_intent, ldf)

            Compiler.compile_vis(ldf, self)
            lux.config.executor.execute([self], ldf)

    def check_not_vislist_intent(self):

        syntaxMsg = (
            "The intent that you specified corresponds to more than one visualization. "
            "Please replace the Vis constructor with VisList to generate a list of visualizations. "
            "For more information, see: https://lux-api.readthedocs.io/en/latest/source/guide/vis.html#working-with-collections-of-visualization-with-vislist"
        )

        for i in range(len(self._intent)):
            clause = self._intent[i]
            if isinstance(clause, str):
                if "|" in clause or "?" in clause:
                    raise TypeError(syntaxMsg)
            if isinstance(clause, list):
                raise TypeError(syntaxMsg)
