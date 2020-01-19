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
    def toJSON(self,currentView=""):
        dobj_dict = {}
        dobj = self.resultsDataObjs[0]
        dobj_dict["currentView"] = Result.currentViewToJSON(dobj,currentView)
        if (dobj.recommendations==[]):
            visCollection = {"action": "Vis Collection",
                "collection":dobj.compiled
            }
            dobj.recommendations.append(visCollection)
        # Recommended Collection
        dobj_dict["recommendations"] = Result.recToJSON(self.resultsJSON)
        return dobj_dict
    
    def display(self, renderer="altair", currentView=""):
        import displayWidget
        widgetJSON = self.toJSON(currentView=currentView)
        widget = displayWidget.DisplayWidget(
            # data=json.loads(self.dataset.df.to_json(orient='records')),
            currentView=widgetJSON["currentView"],
            recommendations=widgetJSON["recommendations"]
        )
        return widget
    @staticmethod
    def currentViewToJSON(currentViewDobj,currentView):
        currentViewSpec = {}
        if (type(currentViewDobj.compiled).__name__ == "DataObj"):
            currentViewSpec = currentViewDobj.compiled.renderVSpec()
        if (type(currentViewDobj.compiled).__name__ == "DataObjCollection"):
            # if the compiled object is a collection, see if we can remove the elements with "?" and generate a Current View
            specifiedDobj = currentViewDobj.getVariableFieldsRemoved()
            if (specifiedDobj.spec!=[]): specifiedDobj.compile(enumerateCollection=False)
            if (currentView!=""):
                currentViewSpec = currentView.compiled.renderVSpec()
            elif (specifiedDobj.isEmpty()):
                currentViewSpec = {}
            else:
                specifiedDobj.compile(enumerateCollection=False)
                currentViewSpec = specifiedDobj.compiled.renderVSpec()
        return currentViewSpec
    @staticmethod
    def recToJSON(recDataObjs):
        recLst = []
        import copy
        recCopy = copy.deepcopy(recDataObjs)
        # for the case of single DataObject display of vis collection 
        if (type(recCopy)!=list): recCopy = [recCopy]
        for idx,rec in enumerate(recCopy):
            if (rec != {}):
                rec["vspec"] = []
                for vis in rec["collection"].collection:
                    chart = vis.renderVSpec()
                    rec["vspec"].append(chart)
                recLst.append(rec)
                # delete DataObjectCollection since not JSON serializable
                del recLst[idx]["collection"]
        return recLst


