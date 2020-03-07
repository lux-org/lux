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
            attributes = []
            xAttribute = view.getObjFromChannel("x")
            yAttribute = view.getObjFromChannel("y")
            zAttribute = view.getObjFromChannel("color")

            if xAttribute and xAttribute[0].attribute:
                attributes.append(xAttribute[0].attribute)
            if yAttribute and yAttribute[0].attribute:
                attributes.append(yAttribute[0].attribute)
            if zAttribute and zAttribute[0].attribute:
                attributes.append(zAttribute[0].attribute)
            view.data = view.data[attributes]
            # TODO (Jaywoo): ExecutionEngine.executeAggregate(view,ldf)
    @staticmethod
    def executeAggregate(view, ldf):
        # TODO (Jaywoo)
        return NotImplemented
    @staticmethod
    def executeFilter(view, ldf):
        filters = view.getFiltersFromSpec()
        if (filters):
            for filter in filters:
                view.data = ldf[ldf[filter.attribute] == filter.value]
        else:
            view.data = ldf