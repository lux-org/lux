def convert2List(x):
	'''
	"a" --> ["a"]
	["a","b"] --> ["a","b"]
	'''
	if type(x) != list:
		return [x]
	else:
		return x


def getAttrsSpecs(specLst):
	specObj = list(filter(lambda x: x.value=="", specLst))
	return specObj


def getFilterSpecs(specLst):
	specObj = list(filter(lambda x: x.value!="", specLst))
	return specObj