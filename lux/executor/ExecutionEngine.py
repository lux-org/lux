from lux.view.ViewCollection import ViewCollection
class ExecutionEngine:
    def __init__(self):
        self.name = "ExecutionEngine"

    def __repr__(self):
        return f"<ExecutionEngine>"
    @staticmethod
    def execute(viewCollection:ViewCollection, ldf):
        '''
        Given a ViewCollection, fetch the data required to render the view
        1) Apply filters
        2) Retreive relevant attribute
        3) return a DataFrame with relevant results
        '''
        for view in viewCollection:
            ExecutionEngine.executeFilter(view, ldf)
            # Select relevant data based on attribute information
            attributes = set([])
            xAttribute = view.getObjFromChannel("x")
            yAttribute = view.getObjFromChannel("y")
            zAttribute = view.getObjFromChannel("color")

            if (xAttribute):
                attributes.add(xAttribute[0].attribute)
            if (yAttribute):
                attributes.add(yAttribute[0].attribute)
            if (zAttribute):
                attributes.add(zAttribute[0].attribute)
            view.data = view.data[list(attributes)]
            ExecutionEngine.executeAggregate(view, ldf)

    @staticmethod
    def executeAggregate(view, ldf):
        # TODO (Jaywoo)
        # get attribute
        # aggreagte in spec
        # horsepower by origin -> lux.spec(horsepower,aggregate = "mean") lux.spec(attribute = Origin)
        # need to add aggregate spec in the compiling stage(inside compiler.determinEncoding)
        xAttr = view.getObjFromChannel("x")[0]
        yAttr = view.getObjFromChannel("y")[0]

        groupbyAttr =""
        if (yAttr.aggregation!=""):
            groupbyAttr = xAttr
            aggFunc = yAttr.aggregation
        if (xAttr.aggregation!=""):
            groupbyAttr = yAttr
            aggFunc = xAttr.aggregation
        
        if (groupbyAttr!=""):
            groupbyResult = view.data.groupby(groupbyAttr.attribute)
            view.data = groupbyResult.agg(aggFunc).reset_index()
    @staticmethod
    def executeFilter(view, ldf):
        filters = view.getFilterSpecs()
        if (filters):
            for filter in filters:
                view.data = ldf[ldf[filter.attribute] == filter.value]
        else:
            view.data = ldf