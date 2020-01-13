import numpy as np

def euclideanDist(query,dobj):

    if dobj.getObjFromChannel("y") and query.getObjFromChannel("y"):

        dobjYAxis = dobj.getObjFromChannel("y")[0].columnName
        queryYAxis = query.getObjFromChannel("y")[0].columnName

        dobjVector = dobj.transformedDataset.df[dobjYAxis].values
        queryVector = query.transformedDataset.df[queryYAxis].values
        return np.linalg.norm(dobjVector - queryVector)
    else:
        print("no y axis detected")
        return 0
