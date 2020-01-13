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
        # Current View (if any)
        # if (type(dobj.compiled).__name__ == "DataObj"):
        #     dobj_dict["currentView"] = dobj.compiled.renderVSpec()
        # if (type(dobj.compiled).__name__ == "DataObjCollection"):
        # if the compiled object is a collection, see if we can remove the elements with "?" and generate a Current View
        specifiedDobj = dobj.getVariableFieldsRemoved()
        if (specifiedDobj.spec!=[]): specifiedDobj.compile(enumerateCollection=False)
        if (currentView!=""):
            dobj_dict["currentView"] = currentView.compiled.renderVSpec()
        elif (specifiedDobj.isEmpty()):
            dobj_dict["currentView"] = {}
        else:
            specifiedDobj.compile(enumerateCollection=False)
            dobj_dict["currentView"] = specifiedDobj.compiled.renderVSpec()
        if (dobj.recommendations==[]):
            visCollection = {"action": "Vis Collection",
                "collection":dobj.compiled
            }
            dobj.recommendations.append(visCollection)
        # Recommended Collection
        dobj_dict["recommendations"] = []
        import copy
        recCopy = copy.deepcopy(self.resultsJSON)
        for idx,rec in enumerate(recCopy):
            if (rec != {}):
                rec["vspec"] = []
                for vis in rec["collection"].collection:
                    chart = vis.renderVSpec()
                    rec["vspec"].append(chart)
                dobj_dict["recommendations"].append(rec)
                # delete DataObjectCollection since not JSON serializable
                del dobj_dict["recommendations"][idx]["collection"]
        # self.resultsJSON = recCopy # set it back to original so that object does not change
        return dobj_dict

    def display(self, renderer="altair", currentView=""):
        # render this data object as: vis, columns, etc.?
        # import widgetDisplay
        # if (renderer=="altair"):
        # 	renderer = AltairRenderer()
        # chart = renderer.createVis(self.compiled)
        # widget = widgetDisplay.Mockup(graphSpecs = [chart.to_dict()])
        # return widget
        # return chart
        import displayWidget
        widgetJSON = self.toJSON(currentView=currentView)
        widget = displayWidget.DisplayWidget(
            # data=json.loads(self.dataset.df.to_json(orient='records')),
            currentView=widgetJSON["currentView"],
            recommendations=widgetJSON["recommendations"]
        )
        return widget