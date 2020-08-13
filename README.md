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
    <a href='https://mybinder.org/v2/gh/lux-org/lux-binder/master'>
        <img src='https://img.shields.io/badge/launch-binder-579ACA.svg?logo=data:image/png;base64,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' alt='Binder'  align="center"/>
    </a>
</p>

Lux is a Python library that makes data science easier by automating certain aspects of the data exploration process. Lux is designed to facilitate faster experimentation with data, even when the user does not have a clear idea of what they are looking for. Lux is integrated with [an interactive Jupyter widget](https://github.com/lux-org/lux-widget) that allows users to quickly browse through large collections of data directly within their Jupyter notebooks.

Here are some [slides](http://dorisjunglinlee.com/files/Zillow_07_2020_Slide.pdf) from a talk on Lux.

Click [here](https://mybinder.org/v2/gh/lux-org/lux-binder/master) to try out Lux on your own in a live notebook! 
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
### Next-step recommendations based on user intent: 

In addition to dataframe visualizations at every step in the exploration, you can specify in Lux the attributes and values you're interested in. Based on this intent information, Lux guides users towards potential next-steps in their exploration.

For example, we might be interested in the attributes `AverageCost` and `SATAverage`.

```python
    df.set_intent(["AverageCost","SATAverage"])
    df
```
<img src="https://github.com/lux-org/lux/blob/master/examples/img/contextRec.gif?raw=true"
     alt="Next-step Recommendations Based on User Context"
     style="width:600px" />
 
 The left-hand side of the widget shows the Current Vis, which corresponds to the visualization based on what the user is interested in. On the right, Lux generates three sets of recommendations, organized as separate tabs on the widget:

 - `Enhance` adds an additional attribute to the current selection, essentially highlighting how additional variables affect the relationship of `AverageCost` and `SATAverage`. We see that if we breakdown the relationship by `FundingModel`, there is a clear separation between public colleges (shown in red) and private colleges (in blue), with public colleges being cheaper to attend and with SAT average of lower than 1400.
 - `Filter` adds a filter to the current selection, while keeping attributes (on the X and Y axes) fixed. These visualizations shows how the relationship of  `AverageCost` and `SATAverage` changes for different subsets of data. For instance, we see that colleges that offer Bachelor's degree as its highest degree offered shows a roughly linear trend between the two variables.
 - `Generalize` removes an attribute to display a more general trend, showing the distributions of `AverageCost` and `SATAverage` on its own. From the `AverageCost` histogram, we see that there are many colleges with average cost of around $20000 per year, corresponding to the bulge we see in the scatterplot view.

 See [this page](https://lux-api.readthedocs.io/en/latest/source/guide/intent.html) more information on additional ways for specifying the intent.

### Easy programmatic access of exported visualization objects: 

Now that we have found some interesting visualizations through Lux, we might be interested in digging into these visualizations a bit more. We can click on one or more visualizations to be exported, so we can programmatically access these visualizations further in Jupyter. Visualizations are represented as `Vis` objects in Lux. These `Vis` objects can be translated into Altair or VegaLite code, so that we can further edit these visualizations.

<img src="https://github.com/lux-org/lux/blob/master/examples/img/export.gif?raw=true"
     alt="Easily exportable visualization object"
     style="width:600px" />

### Quick, on-demand visualizations with the help of automatic encoding: 
We've seen how `Vis`s are automatically generated as part of the recommendations, users can also create their own Vis via the same syntax as specifying the intent. Lux is built on the philosophy that users should always be able to visualize anything they want, without having to think about *how* the visualization should look like. Lux automatically determines the mark and channel mappings based on a set of [best practices](http://hosteddocs.ittoolbox.com/fourshowmeautomaticpresentations.pdf) from [Tableau](https://www.tableau.com). The visualizations are rendered via [Altair](https://github.com/altair-viz/altair/tree/master/altair) into [Vega-Lite](https://github.com/vega/vega-lite) specifications.

```python    
    from lux.vis.Vis import Vis
    newEnglandCost = Vis(["Region=New England","MedianEarnings"])
    newEnglandCost.load(df)
```    

<img src="https://github.com/lux-org/lux/blob/master/examples/img/view.png?raw=true"
     alt="Specified Visualization"
     width="200px" />

### Powerful language for working with collections of visualizations:

Lux provides a powerful abstraction for working with collections of visualizations based on a partially specified queries. Users can provide a list or a wildcard to iterate over combinations of filter or attribute values and quickly browse through large numbers of visualizations. The partial specification is inspired by existing work on intent languages for visualization languages, including [ZQL](https://github.com/vega/compassql) and [CompassQL](https://github.com/vega/compassql).

For example, we might be interested in looking at how the `AverageCost` distribution differs across different `Region`s.

```python    
    from lux.vis.VisList import VisList
    differentRegions = VisList(["Region=?","AverageCost"])
    differentRegions.load(df)
```    

<img src="https://github.com/lux-org/lux/blob/master/examples/img/viewCollection.gif?raw=true"
     alt="Example Vis List"
     style="width:600px" />


To find out more about other features in Lux, see the complete documentation on [ReadTheDocs](https://lux-api.readthedocs.io/).

<!-- ## Quick Installation-->

<!--Install the Python Lux API through [PyPI](https://pypi.org/project/lux-api/):--> 

<!--```bash
pip install lux-api
```-->

<!--Install the Lux Jupyter widget through [npm](https://www.npmjs.com/package/lux-widget): --> 

<!--```bash
npm i lux-widget
```--> 

# Installation 

To setup Lux manually for development purposes, you should clone the two Github repos for Lux: 1) the core Python [Lux API](https://github.com/lux-org/lux)  and 2) the [Jupyter widget frontend](https://github.com/lux-org/lux-widget). 

To install the Python Lux API: 

```bash
    git clone https://github.com/lux-org/lux.git
    cd lux/
    python setup.py install
```

To install the [Lux Jupyter Widget](https://github.com/lux-org/lux-widget): 

```bash
    pip install git+https://github.com/lux-org/lux-widget
    jupyter nbextension install --py luxWidget
    jupyter nbextension enable --py luxWidget
```


<!-- See the [installation page](https://lux-api.readthedocs.io/en/latest/source/getting_started/installation.html) for more information. -->

<!-- For more detailed examples of how to use Lux, check out this demo [notebook](https://github.com/lux-org/lux/blob/master/examples/demo.ipynb).  -->

# Dev Support 
Lux is undergoing active development. Please report any bugs, issues, or requests through [Github Issues](https://github.com/lux-org/lux/issues) or post on the [#help](https://lux-project.slack.com/archives/C0174H16CK0) channel in the <a href="http://lux-project.slack.com/">Lux Slack org</a>.

If you are interested in participating in a user study on Lux, please contact <a href="mailto:dorisjunglinlee@gmail.com">Doris Lee</a>) for more detail.

