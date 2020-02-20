import pandas as pd
class LuxDataFrame(pd.DataFrame):
    # normal properties
    _metadata = ['context','spec']

    def __init__(self,*args, **kw):
        super(LuxDataFrame, self).__init__(*args, **kw)
        self.context = []
        self.spec = []

    @property
    def _constructor(self):
        return LuxDataFrame

    def setContext(self,context):
        self.context = context
    def addToContext(self,context): 
        self.context.extend(context)
    def getContext(self):
        return self.context
    def __repr__(self):
        # TODO: _repr_ gets called from _repr_html, need to get rid of this call
        return ""
    def _repr_html_(self):
        import luxWidget
        import json
        widgetJSON = json.load(open("mockWidgetJSON.json",'r'))
        widget = luxWidget.LuxWidget(
            currentView=widgetJSON["currentView"],
            recommendations=widgetJSON["recommendations"]
        )
        # return widget
        from IPython.display import display
        display(widget)
        
import pandas as pd
global originalDF;
# Keep variable scope of original pandas df
originalDF = pd.core.frame.DataFrame
def delegate(bool):
    if bool:
        pd.DataFrame = pd.io.parsers.DataFrame = pd.core.frame.DataFrame = LuxDataFrame
    else:
        pd.DataFrame = pd.io.parsers.DataFrame = pd.core.frame.DataFrame = originalDF