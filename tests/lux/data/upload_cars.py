import pandas as pd
from sqlalchemy import create_engine
data = pd.read_csv('car.csv')
engine = create_engine("postgresql://postgres:lux@localhost:5432")
data.to_sql(name='cars', con=engine, if_exists = 'replace', index=False)

