class Validator:
    '''
    lux.setContext("Horsepower")
    --> lux.Spec(attr = "Horsepower", type= "attribute")

    lux.setContext("Horsepower", lux.Spec("MilesPerGal",channel="x"))
        --> [lux.Spec(attr ="Horsepower", type= "attribute"), lux.Spec(attr ="MilesPerGal", type= "attribute",channel="x")]

    lux.setContext("Horsepower","Origin=USA")
        --> [lux.Spec(attr ="Horsepower", type= "attribute"), lux.Spec(fAttr = "Origin", fOp = "=", fVal="USA", type= "value")]

    lux.setContext("Horsepower","USA")
        --> [lux.Spec(attr ="Horsepower", type= "attribute"), lux.Spec(fAttr = "Origin", fOp = "=", fVal="USA", type= "value")]

    lux.setContext("Horsepower","Origin=?")
        --> [lux.Spec(attr ="Horsepower", type= "attribute"), lux.Spec(fAttr = "Origin", fOp = "=", fVal="?", type= "valueGroup")]

        -->[[lux.Spec(attr ="Horsepower", type= "attribute"), lux.Spec(fAttr = "Origin", fOp = "=", fVal="USA", type= "value")], 
            [lux.Spec(attr ="Horsepower", type= "attribute"), lux.Spec(fAttr = "Origin", fOp = "=", fVal="UK", type= "value")], 
            [lux.Spec(attr ="Horsepower", type= "attribute"), lux.Spec(fAttr = "Origin", fOp = "=", fVal="Japan", type= "value")] ] 
        
    lux.setContext(["Horsepower","MPG","Acceleration"])
        --> [lux.Spec(attrGroup = ["Horsepower","MPG","Acceleration"], type= "attributeGroup")]
    '''
	def __init__(self):
		self.name = "Validator"

	def __repr__(self):
		return f"<Validator>"
    def validate(self, luxDataFrame):
        # 1. Parse all string specification into Spec objects (nice-to-have)
        # 2. Validate that the parsed specification is corresponds to the content in the LuxDataframe.
        
        

        # lux.setContext(lux.Spec(attr = "Horsepower"))
        # lux.setContext(lux.Spec(attr = "A")) --> Warning

