import lux
import pandas as pd

from lux.interestingness.interestingness import interestingness


df = pd.read_csv("lux/data/car.csv")
df["Year"] = pd.to_datetime(df["Year"], format='%Y') # change pandas dtype for the column "Year" to datetype
# df.setContext([lux.Spec(attribute = "Horsepower"),lux.Spec(attribute = "Year"), lux.Spec(attribute = "Origin", filterOp="=",value = "USA")])



# 0 1 0
df.setContext([lux.Spec(attribute = "Horsepower")])
print(interestingness(df.viewCollection[0],df))

# 1 1 1
df.setContext([lux.Spec(attribute = "Horsepower"), lux.Spec(attribute = "Origin", filterOp="=",value = "USA")])
print(interestingness(df.viewCollection[0],df))

# 1 1 1 set bin size
df.setContext([lux.Spec(attribute = "Horsepower"), lux.Spec(attribute = "Origin", filterOp="=",value = "USA", binSize=20)])
print(interestingness(df.viewCollection[0],df))

# 1 1 0
df.setContext([lux.Spec(attribute = "Horsepower"),lux.Spec(attribute = "Year")])
print(interestingness(df.viewCollection[0],df))

# 0 2 0
df.setContext([lux.Spec(attribute = "Horsepower"),lux.Spec(attribute = "Acceleration")])
print(interestingness(df.viewCollection[0],df))

# 0 2 1
df.setContext([lux.Spec(attribute = "Horsepower"),lux.Spec(attribute = "Acceleration", filterOp=">",value = 10)])
print(interestingness(df.viewCollection[0],df))

