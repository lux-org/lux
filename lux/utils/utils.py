import lux
def convert2List(x):
	'''
	"a" --> ["a"]
	["a","b"] --> ["a","b"]
	'''
	if type(x) != list:
		return [x]
	else:
		return x


def applyDataTransformations(dataset, fAttribute, fVal):
	transformedDataset = lux.Dataset(filename=dataset.filename, schema=dataset.schema)
	transformedDataset.df = dataset.df[dataset.df[fAttribute] == fVal]
	return transformedDataset