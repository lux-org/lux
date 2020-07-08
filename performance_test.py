import pandas as pd
import lux

# df = pd.read_csv("lux/data/cars.csv")
df = pd.read_parquet("../../Desktop/Demo Data/parquet/amazon-reviews/product_category=Furniture/part-00000-495c48e6-96d6-4650-aa65-3c36a3516ddd.c000.snappy.parquet")
df = df.sample(20000)
# df.setExecutorType("Pandas")
# df["Year"] = pd.to_datetime(df["Year"], format='%Y') # change pandas dtype for the column "Year" to datetype
df.computeStats()
df.computeDatasetMetadata()
df.showMore()
