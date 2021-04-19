import pandas as pd
import psycopg2
import csv

conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=lux")
cur = conn.cursor()
cur.execute(
    """
	DROP TABLE IF EXISTS aug_test_table
	"""
)
# create car table in postgres database
cur.execute(
    """
    CREATE TABLE aug_test_table(
    enrollee_id integer,
    city text,
    city_development_index numeric,
    gender text,
    relevent_experience text,
    enrolled_university text,
    education_level text,
    major_discipline text,
    experience text,
    company_size text,
    company_type text,
    last_new_job text,
    training_hours integer
)
"""
)

# open car.csv and read data into database
import urllib.request

target_url = "https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/aug_test.csv"
for line in urllib.request.urlopen(target_url):
    decoded = line.decode("utf-8")
    if "enrollee_id,city,city_development_index" not in decoded:
        cur.execute(
            "INSERT INTO aug_test_table VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            decoded.split(","),
        )
conn.commit()
