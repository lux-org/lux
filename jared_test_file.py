import lux
import pandas as pd


df = pd.read_csv("lux/data/car.csv")
df["Year"] = pd.to_datetime(df["Year"], format='%Y') # change pandas dtype for the column "Year" to datetype
# df.setContext([lux.Spec(attribute = "Horsepower"),lux.Spec(attribute = "Year"), lux.Spec(attribute = "Origin", filterOp="=",value = "USA")])
df.setContext([lux.Spec(attribute = "Horsepower")])
from lux.interestingness.interestingness import interestingness
interestingness(df.viewCollection[0],df)

df.setContext([lux.Spec(attribute = "Horsepower"),lux.Spec(attribute = "Year")])
interestingness(df.viewCollection[0],df)

# df.showMore()
# ExecutionEngine.execute(df.viewCollection,df)
