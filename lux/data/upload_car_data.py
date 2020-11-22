import pandas as pd
import psycopg2
import csv

conn = psycopg2.connect("host=localhost dbname=postgres_db user=postgres password=lux")
cur = conn.cursor()
cur.execute(
    """
	DROP TABLE IF EXISTS car
	"""
)
# create car table in postgres database
cur.execute(
    """
    CREATE TABLE car(
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
with open("lux/data/car.csv", "r") as f:
    reader = csv.reader(f)
    next(reader)  # Skip the header row.
    i = 0
    for row in reader:
        cur.execute("INSERT INTO car VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", row)

conn.commit()
