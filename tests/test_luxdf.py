import lux

import pandas as pd

df = pd.read_csv("lux/data/car.csv")

df.setContext([lux.Spec(attribute="Horsepower"), lux.Spec(attributeGroup="?")])
df.setContext([lux.Spec(attribute="Horsepower"), lux.Spec(attribute="Origin",valueGroup="?")])
df.setContext([lux.Spec(attribute="Horsepower"), lux.Spec(attribute="MilesPerGal")])
df.getContext()