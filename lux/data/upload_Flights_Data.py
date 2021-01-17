import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import csv

import psycopg2
conn = psycopg2.connect("host=localhost dbname=adventureworks user=postgres password=dbadmin")
cur = conn.cursor()
# cur.execute("""
# 	DROP TABLE IF EXISTS flights
# 	""")

#create flights table in postgres database
cur.execute("""
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
""")

#open flights.csv and read data into database
with open('flights.csv', 'r') as f:
	reader = csv.reader(f)
	next(reader) # Skip the header row.
	i = 0
	for row in reader:
		if i%50000 == 0:
			print(i)
		i+=1
		#print(row)
		cur.execute(
		"INSERT INTO flights VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
		row
	)

conn.commit()