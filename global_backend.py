class backend:
    def __init__(self):
        self.backend = "pandas"
    
    def set_back(self,type):
        self.backend = type
        return self.backend