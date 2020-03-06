class Result:
    def __init__(self):
        self.resultsDataObjs = [] #Putting data objects here so that it can be further accessed.
        self.resultsJSON = [] # DataObject separate from JSON since not serializable

    def __repr__(self):
        return f"Result[{self.resultsJSON}]"
    def mergeResult(self,result2):
        self.resultsDataObjs.extend(result2.resultsDataObjs)
        self.resultsJSON.extend(result2.resultsJSON)
    def addResult(self,recommendation,dobj):
        self.resultsJSON.append(recommendation)
        self.resultsDataObjs.append(dobj)
    