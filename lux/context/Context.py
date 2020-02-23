class Context:
	'''
	Context Object represents one or a group of datapoints (columns) in the Dataset.
	'''
    def __init__(self, specLst):
        self.specLst = specLst
        # self.compile()
    # def addContext(spec): # Should go inside dataframe
    #     self.context.specLst.append(spec)
    def __repr__(self):
        return NotImplemented