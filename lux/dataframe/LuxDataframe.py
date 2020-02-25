import pandas as pd
global originalDF;

originalDF = pd.core.frame.DataFrame

class LuxDataFrame(pd.DataFrame):
    # normal properties
    _metadata = ['context','spec']

    def __init__(self,*args, **kw):
        super(LuxDataFrame, self).__init__(*args, **kw)
        self.context = []
        self.spec = []

    @property
    def _constructor(self):
        return LuxDataFrame

    def indicate(self,luxThing):
        self.context.append(luxThing)




