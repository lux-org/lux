from dataObj.DataObjCollection import DataObjCollection
def getSelectedDobjs(dobj,widget):
    return DataObjCollection([dobj.compiled.collection[index] for index in widget.selected_graphID])
def showJSONspec(dictSpec):
    from utils.renderjson import RenderJSON
    import json
    if (type(dictSpec)!=dict):
        parsed = json.loads(dictSpec)
    else:
        parsed = dictSpec
    return RenderJSON(parsed)