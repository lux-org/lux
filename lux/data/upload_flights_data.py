import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import csv

import psycopg2

conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
cur = conn.cursor()
cur.execute(
    """
	DROP TABLE IF EXISTS flights
	"""
)

# create flights table in postgres database
cur.execute(
    """
    CREATE TABLE flights(
    year integer,
    month text,
    day integer,
    weekday integer,
    carrier text,
    origin text,
    destination text,
    arrivaldelay integer,
    depaturedelay integer,
    weatherdelay integer,
    distance integer
)
"""
)

# open car.csv and read data into database
import urllib.request

target_url = "https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/flights.csv"
for line in urllib.request.urlopen(target_url):
    decoded = line.decode("utf-8")
    if "day,weekday,carrier,origin" not in decoded:
        cur.execute(
            "INSERT INTO flights VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", decoded.split(",")
        )
conn.commit()
