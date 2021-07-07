postgres_template = """preview_query:SELECT * from {table_name} LIMIT {num_rows}
length_query:SELECT COUNT(1) as length FROM {table_name} {where_clause}
sample_query:SELECT * FROM {table_name} {where_clause} ORDER BY random() LIMIT {num_rows}
scatter_query:SELECT {columns} FROM {table_name} {where_clause}
colored_barchart_counts:SELECT "{groupby_attr}", "{color_attr}", COUNT("{groupby_attr}") FROM {table_name} {where_clause} GROUP BY "{groupby_attr}", "{color_attr}"
colored_barchart_average:SELECT "{groupby_attr}", "{color_attr}", AVG("{measure_attr}") as "{measure_attr}" FROM {table_name} {where_clause} GROUP BY "{groupby_attr}", "{color_attr}"
colored_barchart_sum:SELECT "{groupby_attr}", "{color_attr}", SUM("{measure_attr}") as "{measure_attr}" FROM {table_name} {where_clause} GROUP BY "{groupby_attr}", "{color_attr}"
colored_barchart_max:SELECT "{groupby_attr}", "{color_attr}", MAX("{measure_attr}") as "{measure_attr}" FROM {table_name} {where_clause} GROUP BY "{groupby_attr}", "{color_attr}"
barchart_counts:SELECT "{groupby_attr}", COUNT("{groupby_attr}") FROM {table_name} {where_clause} GROUP BY "{groupby_attr}"
barchart_average:SELECT "{groupby_attr}", AVG("{measure_attr}") as "{measure_attr}" FROM {table_name} {where_clause} GROUP BY "{groupby_attr}"
barchart_sum:SELECT "{groupby_attr}", SUM("{measure_attr}") as "{measure_attr}" FROM {table_name} {where_clause} GROUP BY "{groupby_attr}"
barchart_max:SELECT "{groupby_attr}", MAX("{measure_attr}") as "{measure_attr}" FROM {table_name} {where_clause} GROUP BY "{groupby_attr}"
histogram_counts:SELECT width_bucket, COUNT(width_bucket) FROM (SELECT width_bucket(CAST ("{bin_attribute}" AS FLOAT), '{upper_edges}') FROM {table_name} {where_clause}) as Buckets GROUP BY width_bucket ORDER BY width_bucket
heatmap_counts:SELECT width_bucket1, width_bucket2, count(*) FROM (SELECT width_bucket(CAST ("{x_attribute}" AS FLOAT), '{x_upper_edges_string}') as width_bucket1, width_bucket(CAST ("{y_attribute}" AS FLOAT), '{y_upper_edges_string}') as width_bucket2 FROM {table_name} {where_clause}) as foo GROUP BY width_bucket1, width_bucket2
table_attributes_query:SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = '{table_name}'
min_max_query:SELECT MIN("{attribute}") as min, MAX("{attribute}") as max FROM {table_name}
cardinality_query:SELECT Count(Distinct("{attribute}")) FROM {table_name} WHERE "{attribute}" IS NOT NULL
unique_query:SELECT Distinct("{attribute}") FROM {table_name} WHERE "{attribute}" IS NOT NULL
datatype_query:SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' AND COLUMN_NAME = '{attribute}'"""

mysql_template = """preview_query:SELECT * from {table_name} LIMIT {num_rows}
length_query:SELECT COUNT(*) as length FROM {table_name} {where_clause}
sample_query:SELECT * FROM {table_name} {where_clause} LIMIT {num_rows}
scatter_query:SELECT {columns} FROM {table_name} {where_clause}
colored_barchart_counts:SELECT {groupby_attr}, {color_attr}, COUNT({groupby_attr}) as count FROM {table_name} {where_clause} GROUP BY {groupby_attr}, {color_attr}
colored_barchart_average:SELECT {groupby_attr}, {color_attr}, AVG({measure_attr}) as {measure_attr} FROM {table_name} {where_clause} GROUP BY {groupby_attr}, {color_attr}
colored_barchart_sum:SELECT {groupby_attr}, {color_attr}, SUM({measure_attr}) as {measure_attr} FROM {table_name} {where_clause} GROUP BY {groupby_attr}, {color_attr}
colored_barchart_max:SELECT {groupby_attr}, {color_attr}, MAX({measure_attr}) as {measure_attr} FROM {table_name} {where_clause} GROUP BY {groupby_attr}, {color_attr}
barchart_counts:SELECT {groupby_attr}, COUNT({groupby_attr}) as count FROM {table_name} {where_clause} GROUP BY {groupby_attr}
barchart_average:SELECT {groupby_attr}, AVG({measure_attr}) as {measure_attr} FROM {table_name} {where_clause} GROUP BY {groupby_attr}
barchart_sum:SELECT {groupby_attr}, SUM({measure_attr}) as {measure_attr} FROM {table_name} {where_clause} GROUP BY {groupby_attr}
barchart_max:SELECT {groupby_attr}, MAX({measure_attr}) as {measure_attr} FROM {table_name} {where_clause} GROUP BY {groupby_attr}
histogram_counts:SELECT width_bucket, count(width_bucket) as count from (SELECT ({bucket_cases}) as width_bucket from {table_name} {where_clause}) as buckets GROUP BY width_bucket order by width_bucket
heatmap_counts:SELECT width_bucket1, width_bucket2, count(*) as count FROM (SELECT ({bucket_cases1}) as width_bucket1, ({bucket_cases2}) as width_bucket2 FROM {table_name} {where_clause}) as labeled_data GROUP BY width_bucket1, width_bucket2
table_attributes_query:SELECT COLUMN_NAME as column_name FROM INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = '{table_name}'
min_max_query:SELECT MIN({attribute}) as min, MAX({attribute}) as max FROM {table_name}
cardinality_query:SELECT COUNT(Distinct({attribute})) as count FROM {table_name} WHERE {attribute} IS NOT NULL
unique_query:SELECT Distinct({attribute}) FROM {table_name} WHERE {attribute} IS NOT NULL
datatype_query:SELECT DATA_TYPE as data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' AND COLUMN_NAME = '{attribute}'"""
