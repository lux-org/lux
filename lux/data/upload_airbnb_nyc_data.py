import pandas as pd
import psycopg2
import csv

from sqlalchemy import create_engine


data = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/airbnb_nyc.csv")
engine = create_engine("postgresql://postgres:lux@localhost:5432")
data.to_sql(name="airbnb", con=engine, if_exists="replace", index=False)
