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

import typing


class Clause:
    """
    Clause is the object representation of a single unit of the specification.
    """

    def __init__(
        self,
        description: typing.Union[str, list] = "",
        attribute: typing.Union[str, list] = "",
        value: typing.Union[str, list] = "",
        filter_op: str = "=",
        channel: str = "",
        data_type: str = "",
        data_model: str = "",
        aggregation: typing.Union[str, callable] = "",
        bin_size: int = 0,
        weight: float = 1,
        sort: str = "",
        timescale: str = "",
        exclude: typing.Union[str, list] = "",
    ):
        """

        Parameters
        ----------
        description : typing.Union[str,list], optional
                Convenient shorthand description of specification, parser parses description into other properties (attribute, value, filter_op), by default ""
        attribute : typing.Union[str,list], optional
                Specified attribute(s) of interest, by default ""
                By providing a list of attributes (e.g., [Origin,Brand]), user is interested in either one of the attribute (i.e., Origin or Brand).
        value : typing.Union[str,list], optional
                Specified value(s) of interest, by default ""
                By providing a list of values (e.g., ["USA","Europe"]), user is interested in either one of the attribute (i.e., USA or Europe).
        filter_op : str, optional
                Filter operation of interest.
                Possible values: '=', '<', '>', '<=', '>=', '!=', by default "="
        channel : str, optional
                Encoding channel where the specified attribute should be placed.
                Possible values: 'x','y','color', by default ""
        data_type : str, optional
                Data type for the specified attribute.
                Possible values: 'nominal', 'quantitative','temporal', by default ""
        data_model : str, optional
                Data model for the specified attribute
                Possible values: 'dimension', 'measure', by default ""
        aggregation : typing.Union[str,callable], optional
                Aggregation function for specified attribute, by default "" set as 'mean'
                Possible values: 'sum','mean', and others string shorthand or functions supported by Pandas.aggregate (https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.aggregate.html), including numpy aggregation functions (e.g., np.ptp), by default ""
                Input `None` means no aggregation should be applied (e.g., data has been pre-aggregated)
        bin_size : int, optional
                Number of bins for histograms, by default 0
        weight : float, optional
                A number between 0 and 1 indicating the importance of this Clause, by default 1
        timescale : str, optional
                If data type is temporal, indicate whether temporal associated with timescale (if empty, then plot overall).
                If timescale is present, the line chart axis is based on ordinal data type (non-date axis).
        sort : str, optional
                Specifying whether and how the bar chart should be sorted
                Possible values: 'ascending', 'descending', by default ""
        """
        # Descriptor
        self.description = description
        # Description gets compiled to attribute, value, filter_op
        self.attribute = attribute
        self.value = value
        self.filter_op = filter_op
        # self.parseDescription()
        # Properties
        self.channel = channel
        self.data_type = data_type
        self.data_model = data_model
        self.set_aggregation(aggregation)
        self.bin_size = bin_size
        self.weight = weight
        self.sort = sort
        self.timescale = timescale
        self.exclude = exclude

    def get_attr(self):
        return self.attribute

    def copy_clause(self):
        copied_clause = Clause()
        copied_clause.__dict__ = self.__dict__.copy()  # just a shallow copy
        return copied_clause

    def set_aggregation(self, aggregation: typing.Union[str, callable]):
        """
        Sets the aggregation function of Clause,
        while updating _aggregation_name internally

        Parameters
        ----------
        aggregation : typing.Union[str,callable]
        """
        self.aggregation = aggregation
        # If aggregation input is a function (e.g., np.std), get the string name of the function for plotting
        if hasattr(self.aggregation, "__name__"):
            self._aggregation_name = self.aggregation.__name__
        else:
            self._aggregation_name = self.aggregation

    def to_string(self):
        if isinstance(self.attribute, list):
            clauseStr = "|".join(self.attribute)
        elif self.value == "":
            clauseStr = str(self.attribute)
        else:
            clauseStr = f"{self.attribute}{self.filter_op}{self.value}"
        return clauseStr

    def __repr__(self):
        attributes = []
        if self.description != "":
            attributes.append(f"         description: {self.description}")
        if self.channel != "":
            attributes.append(f"         channel: {self.channel}")
        if self.attribute != "":
            attributes.append(f"         attribute: {str(self.attribute)}")
        if self.filter_op != "=":
            attributes.append(f"         filter_op: {str(self.filter_op)}")
        if self.aggregation != "" and self.aggregation is not None:
            attributes.append("         aggregation: " + self._aggregation_name)
        if self.value != "" or len(self.value) != 0:
            attributes.append(f"         value: {str(self.value)}")
        if self.data_model != "":
            attributes.append(f"         data_model: {self.data_model}")
        if len(self.data_type) != 0:
            attributes.append(f"         data_type: {str(self.data_type)}")
        if self.bin_size != 0:
            attributes.append(f"         bin_size: {str(self.bin_size)}")
        if len(self.exclude) != 0:
            attributes.append(f"         exclude: {str(self.exclude)}")
        attributes[0] = "<Clause" + attributes[0][7:]
        attributes[len(attributes) - 1] += " >"
        return ",\n".join(attributes)
