import pandas as pd
import psycopg2
import csv

from sqlalchemy import create_engine

data = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/car.csv")
engine = create_engine("postgresql://postgres:lux@localhost:5432")
data.to_sql(name="car", con=engine, if_exists="replace", index=False)

conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
cur = conn.cursor()
cur.execute(
    """
    DROP TABLE IF EXISTS cars
    """
)
# create car table in postgres database
cur.execute(
    """
    CREATE TABLE cars(
    name text,
    milespergal numeric,
    cylinders integer,
    displacement numeric,
    horsepower integer,
    weight integer,
    acceleration numeric,
    year integer,
    origin text,
    brand text
)
"""
)

# open car.csv and read data into database
import urllib.request

target_url = "https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/car.csv"
for line in urllib.request.urlopen(target_url):
    decoded = line.decode("utf-8")
    if "Name,MilesPerGal,Cylinders" not in decoded:
        cur.execute(
            "INSERT INTO cars VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", decoded.split(",")
        )
conn.commit()
