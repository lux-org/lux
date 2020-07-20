<p align="center"><a href="#"><img width=77% alt="" src="https://github.com/lux-org/lux/blob/master/examples/img/logo.png?raw=true"></a></p>
<h2 align="center">A Python API for Intelligent Visual Discovery</h2>

<p align="center">
    <a href="https://travis-ci.com/lux-org/lux">
        <img alt="Build Status" src="https://travis-ci.com/lux-org/lux.svg?branch=master" align="center">
    </a>
    <a href="https://badge.fury.io/py/lux-api">
        <img src="https://badge.fury.io/py/lux-api.svg" alt="PyPI version" height="18" align="center">
    </a>
    <a href='https://lux-api.readthedocs.io/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/lux-api/badge/?version=latest' alt='Documentation Status'  align="center"/>
    </a>
    <a href='http://lux-project.slack.com/'>
        <img src='https://img.shields.io/static/v1?label=chat&logo=slack&message=Slack&color=brightgreen' alt='Slack'  align="center"/>
    </a>
</p>

Lux is a Python library that makes data science easier by automating certain aspects of the data exploration process. Lux is designed to facilitate faster experimentation with data, even when the user does not have a clear idea of what they are looking for. Lux is integrated with [an interactive Jupyter widget](https://github.com/lux-org/lux-widget) that allows users to quickly browse through large collections of data directly within their Jupyter notebooks.

Here are some [slides](http://dorisjunglinlee.com/files/RISE_Winter_Retreat_Slides.pdf) from a talk on Lux.


# Getting Started

To start using Lux, simply add an additional import statement alongside your Pandas import.

```python    
import lux
import pandas as pd
```

Then, Lux can be used as-is, without modifying any of your existing Pandas code. Here, we use Pandas's [read_csv](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html) command to load in a [dataset of colleges](https://collegescorecard.ed.gov/data/documentation/) and their properties.

```python    
    df = pd.read_csv("college.csv")
    df
```

<img src="https://github.com/lux-org/lux/blob/master/examples/img/basicDemo.gif?raw=true"
     alt="Basic recommendations in Lux"
     style="width:900px" />

Voila! Here's a set of visualizations that you can now use to explore your dataset further!

<!-- # Features
Lux provides a suite of capabilities that enables users to effortlessly discover visual insights from their data. -->

<!-- Lux guides users to potential next-steps in their exploration. -->
### Next-step recommendations based on user context: 

In addition to dataframe visualizations at every step in the exploration, you can specify in Lux the attributes and values you're interested in. Based on this context information, Lux guides users towards potential next-steps in their exploration.

For example, we might be interested in the attributes `AverageCost` and `SATAverage`.

```python
    df.set_context(["AverageCost","SATAverage"])
    df
```
<img src="https://github.com/lux-org/lux/blob/master/examples/img/contextRec.gif?raw=true"
     alt="Next-step Recommendations Based on User Context"
     style="width:600px" />
 
 The left-hand side of the widget shows the Current Vis, which corresponds to the visualization based on what the user is interested in. On the right, Lux generates three sets of recommendations, organized as separate tabs on the widget:

 - `Enhance` adds an additional attribute to the current selection, essentially highlighting how additional variables affect the relationship of `AverageCost` and `SATAverage`. We see that if we breakdown the relationship by `FundingModel`, there is a clear separation between public colleges (shown in red) and private colleges (in blue), with public colleges being cheaper to attend and with SAT average of lower than 1400.
 - `Filter` adds a filter to the current selection, while keeping attributes (on the X and Y axes) fixed. These visualizations shows how the relationship of  `AverageCost` and `SATAverage` changes for different subsets of data. For instance, we see that colleges that offer Bachelor's degree as its highest degree offered shows a roughly linear trend between the two variables.
 - `Generalize` removes an attribute to display a more general trend, showing the distributions of `AverageCost` and `SATAverage` on its own. From the `AverageCost` histogram, we see that there are many colleges with average cost of around $20000 per year, corresponding to the bulge we see in the scatterplot view.

 See [this page](https://lux-api.readthedocs.io/en/latest/source/guide/spec.html) more information on additional ways for specifying the context.

### Easy programmatic access of exported visualization objects: 

Now that we have found some interesting visualizations through Lux, we might be interested in digging into these visualizations a bit more. We can click on one or more visualizations to be exported, so we can programmatically access these visualizations further in Jupyter. Visualizations are represented as `Vis` objects in Lux. These `Vis` objects can be translated into Altair or VegaLite code, so that we can further edit these visualizations.

<img src="https://github.com/lux-org/lux/blob/master/examples/img/export.gif?raw=true"
     alt="Easily exportable visualization object"
     style="width:600px" />

### Quick, on-demand visualizations with the help of automatic encoding: 
We've seen how `Vis`s are automatically generated as part of the recommendations, users can also create their own Vis via the same syntax as specifying the context. Lux is built on the philosophy that users should always be able to visualize anything they want, without having to think about *how* the visualization should look like. Lux automatically determines the mark and channel mappings based on a set of [best practices](http://hosteddocs.ittoolbox.com/fourshowmeautomaticpresentations.pdf) from [Tableau](https://www.tableau.com). The visualizations are rendered via [Altair](https://github.com/altair-viz/altair/tree/master/altair) into [Vega-Lite](https://github.com/vega/vega-lite) specifications.

```python    
    from lux.vis.Vis import Vis
    newEnglandCost = Vis(["Region=New England","MedianEarnings"])
    newEnglandCost.load(df)
```    

<img src="https://github.com/lux-org/lux/blob/master/examples/img/view.png?raw=true"
     alt="Specified Visualization"
     width="200px" />

### Powerful language for working with collections of visualizations:

Lux provides a powerful abstraction for working with collections of visualizations based on a partially specified queries. Users can provide a list or a wildcard to iterate over combinations of filter or attribute values and quickly browse through large numbers of visualizations. The partial specification is inspired by existing work on query languages for visualization languages, including [ZQL](https://github.com/vega/compassql) and [CompassQL](https://github.com/vega/compassql).

For example, we might be interested in looking at how the `AverageCost` distribution differs across different `Region`s.

```python    
    from lux.vis.VisCollection import VisCollection
    differentRegions = VisCollection(["Region=?","AverageCost"])
    differentRegions.load(df)
```    

<img src="https://github.com/lux-org/lux/blob/master/examples/img/viewCollection.gif?raw=true"
     alt="Example Vis Collection"
     style="width:600px" />


To find out more about other features in Lux, see the complete documentation on [ReadTheDocs](https://lux-api.readthedocs.io/).

## Quick Installation

Install the Python Lux API through [PyPI](https://pypi.org/project/lux-api/): 

```bash
pip install lux-api
```

Install the Lux Jupyter widget through [npm](https://www.npmjs.com/package/lux-widget): 

```bash
npm i lux-widget
```

See the [installation page](https://lux-api.readthedocs.io/en/latest/source/getting_started/installation.html) for more information.

<!-- For more detailed examples of how to use Lux, check out this demo [notebook](https://github.com/lux-org/lux/blob/master/examples/demo.ipynb).  -->

# Dev Support 
Lux is undergoing active development. Please report any bugs, issues, or requests through [Github Issues](https://github.com/lux-org/lux/issues) or post on the #help channel in the <a href="http://lux-project.slack.com/">Lux Slack org</a>.

If you are interested in participating in a user study on Lux, please contact Doris Lee (<a href="mailto:dorislee@berkeley.edu">dorislee@berkeley.edu</a>) for more detail.

