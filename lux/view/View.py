class View:
    '''
    View Object represents a collection of fully fleshed out specifications required for data fetching and visualization.
    '''


    def __init__(self, specifiedSpecLst,title=""):
        self.specLst = specifiedSpecLst
        self.title = title
        self.mark = ""

    def __repr__(self):
        return f"<View: Mark: {self.mark} Specs: {str(self.specLst)}>"

    def getObjFromChannel(self, channel):
        specObj = list(filter(lambda x: x.channel == channel if hasattr(x, "channel") else False, self.specLst))
        return specObj

    def getObjByDataModel(self, dmodel):
        return list(filter(lambda x: x.dataModel == dmodel if hasattr(x, "dataModel") else False, self.specLst))

    def removeColumnFromSpec(self, columnName):
        self.spec = list(filter(lambda x: x.columnName != columnName, self.specLst))
    '''
    Possibly add more helper functions for retrieving information fro specified SpecLst 
    '''