class View:
    '''
    View Object represents a collection of fully fleshed out specifications required for data fetching and visualization.
    '''


    def __init__(self, specifiedSpecLst):
        self.specLst = specifiedSpecLst

    def __repr__(self):
        return f"<View: {str(self.specLst)}>"


    '''
    Possibly add more helper functions for retrieving information fro specified SpecLst 
    '''