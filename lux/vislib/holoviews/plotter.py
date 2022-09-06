#  SPDX-FileCopyrightText: Copyright (c) 2022, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


import pandas as pd
import holoviews as hv
import numpy as np
import datetime
hv.extension('bokeh')
import re
import cudf
import time
import cupy
import numpy
from holoviews.operation.datashader import datashade,dynspread, rasterize,spread
from collections import Counter
import geopandas as gpd
import warnings
warnings.filterwarnings('ignore')

def plots(df,dat):
    
    state_codes = {
    'WA': '53', 'DE': '10', 'DC': '11', 'WI': '55', 'WV': '54', 'HI': '15',
    'FL': '12', 'WY': '56', 'PR': '72', 'NJ': '34', 'NM': '35', 'TX': '48',
    'LA': '22', 'NC': '37', 'ND': '38', 'NE': '31', 'TN': '47', 'NY': '36',
    'PA': '42', 'AK': '02', 'NV': '32', 'NH': '33', 'VA': '51', 'CO': '08',
    'CA': '06', 'AL': '01', 'AR': '05', 'VT': '50', 'IL': '17', 'GA': '13',
    'IN': '18', 'IA': '19', 'MA': '25', 'AZ': '04', 'ID': '16', 'CT': '09',
    'ME': '23', 'MD': '24', 'OK': '40', 'OH': '39', 'UT': '49', 'MO': '29',
    'MN': '27', 'MI': '26', 'RI': '44', 'KS': '20', 'MT': '30', 'MS': '28',
    'SC': '45', 'KY': '21', 'OR': '41', 'SD': '46'
}
    
    dat=pd.DataFrame(dat)
    df = df.to_cudf()
    adder = False
    flag = False
    left_name="name"
    grph_num = 1
    for words in dat['collection']:
        lets = str(words).split("\n")
        for let in lets:
            res = re.findall(r'\w+', let)
            graph = res[-4]
            form = ""
            if graph =="histogram":
                #print("histogram")
                #starting = time.time()
                xlabel = res[3]
                ylabel = res[6]
                x = cudf.Series(df[xlabel])
                x = cupy.fromDlpack(x.to_dlpack())
                frequencies, edges = cupy.histogram(x, bins=10)
                if abs(max(edges))>10000: form = '%.1e'
                curve=hv.Histogram((edges.get(), frequencies.get())).opts(axiswise=True,  xformatter=form, xlabel=xlabel, ylabel=ylabel, title = graph +" : "+str(grph_num), tools=["hover", ])#yformatter='%.1e',
                grph_num+=1
                if not adder: adder = curve
                else: adder+=curve
                #print("time in histogram :", time.time() -starting)
            elif graph =="bar":
                #print("bar")
                #starting = time.time()
                xlabel ="Records"
                ylabel = res[5]
                x=df.groupby(ylabel).count()
                x.reset_index(inplace=True)
                if x[ylabel].shape[0]>10: 
                    a=time.time()
                    x=x.sort_values(x.columns[1],ascending=False)
                    lis = list(zip(x[ylabel].iloc[:10].values_host, x.iloc[:10, 1].values_host))
                    #print("extra inverse bar", time.time()-a)
                else: lis = list(zip(x[ylabel].values_host, x.iloc[:, 1].values_host))
                reduced_lis=[]
                # for i in range(len(lis)):
                #     print(lis[i][0])
                #     if (lis[i][0].isalpha() and len(lis[i][0])>15):
                #         reduced_lis.append((lis[i][0][:15],lis[i][1]))
                if abs(x.iloc[:, 1].max())>10000: form = '%.1e'
                curve = hv.Bars(lis).opts(invert_axes=True).opts(axiswise=True, xlabel=ylabel, ylabel =xlabel,xformatter=form, title = graph +" : "+str(grph_num), tools=["hover", ])
                grph_num+=1
                if not adder: adder = curve
                else: adder+=curve
            elif graph =="line":
                #print("line")
                #starting = time.time()
                xlabel = res[2]
                factor = re.search(xlabel + '(.*)y', "".join(res)).group(1)
                ylabel = "Records"
                if factor == 'dayofweek':
                    x = cudf.DatetimeIndex(df[xlabel])
                    x = cudf.DataFrame(x.dayofweek, columns = ["date"])
                    x["count"] = x['date']
                elif factor =='month':
                    x = cudf.DatetimeIndex(df[xlabel])
                    x = cudf.DataFrame(x.month, columns = ["date"])
                    x["count"] = x['date']
                elif factor =="year":
                    x = cudf.DatetimeIndex(df[xlabel])
                    x = cudf.DataFrame(x.year, columns = ["date"])
                    x["count"] = x['date']
                else:
                    x = df.rename(columns={xlabel: "date"})
                    cols = df.columns
                    for c in cols: 
                        if c!='date':
                            extra_name=c
                            break
                    x = x[['date',extra_name]]
                    x = x.rename(columns={extra_name: "count"})

                x = x.groupby("date").count()
                x.reset_index(inplace=True)
                x = x.sort_values('date')
                x.reset_index(inplace=True)
                x.reset_index(inplace=True)
                lis = list(zip(x['level_0'].values_host, x['count'].values_host)) if len(factor)==0 else list(zip(x['date'].values_host, x['count'].values_host))
                curve = rasterize(hv.Curve(lis)).opts(axiswise=True,yformatter='%.1e', xlabel=xlabel, ylabel=ylabel , title = graph +" : "+str(grph_num),tools=["hover", ])
                grph_num+=1
                if adder==False: adder = curve
                else: adder+=curve
                #print("time in linecurve :", time.time() -starting)
            elif graph == "scatter":
                #print("scatter")
                #starting = time.time()
                xlabel = res[2]
                ylabel = res[4]
                x = cudf.DataFrame(df[xlabel],columns=[xlabel])
                y = cudf.DataFrame(df[ylabel],columns=[ylabel])
                z = cudf.concat([x,y],axis=1)
                #if abs(x.max())>10000: form = '%.1e'
                curve = rasterize(hv.Scatter(z)).opts(axiswise=True, xformatter = form, xlabel=xlabel, ylabel=ylabel, title = graph +" : "+str(grph_num), tools=["hover", ],cmap=['blue'])#,threshold=0.75)#
                grph_num+=1
                if adder==False: adder = curve
                else: adder+=curve
                #print("time in scatterplot :", time.time() -starting)
            elif graph =="geographical":
#                 #print("geo")
#                 #starting = time.time()
#                 geo = res[2]
#                 vals = res[5]
#                 #print(geo)
#                 x=df.groupby(geo).mean()
#                 x.reset_index(inplace=True)
#                 if not flag:
#                     if geo in ["states","state","States","State", "STATES", "STATE"]:
#                         geography = gpd.read_file("lux/vislib/holoviews/us-states.json")
#                         if isinstance(x[geo].iloc[0],numpy.int64):
#                             left_name = "fips_num"
#                             geography[left_name] = geography["id"].apply(lambda x: int(state_codes[x]))
#                         geography_pop = geography.merge(x.to_pandas(), left_on=left_name, right_on=geo)
                        
#                     elif geo in ["Country", "COUNTRY", "country", "COUNTRIES","countries", "Countries"]:
#                         geography = gpd.read_file("lux/vislib/holoviews/countries.geojson")
#                         geography_pop = geography.merge(x.to_pandas(), left_on="ADMIN", right_on=geo)
#                         # geography_pop=geography_pop.drop(['ADMIN', "ISO_A3"], axis=1)
#                         # geography_pop =  geography_pop.reset_index()
#                         # geography_pop['index'] = geography_pop['index'].astype('float64')
#                         # print(geography_pop.dtypes)
#                         # print(geography_pop)
#                     flag =True
#                 if geo in ["states","state","States","State", "STATES", "STATE"]:
                    
#                     curve = rasterize(hv.Polygons(data=geography_pop, vdims=[vals])).opts(axiswise=True, xlim=(-170, -60), ylim=(10,75),  height=300, width=400, title=vals+" : "+str(grph_num), tools=["hover", ])#, colorbar=True, colorbar_position="right" #geo
#                 elif geo in ["Country", "COUNTRY", "country", "COUNTRIES","countries", "Countries"]:
                    
#                     curve =  rasterize(hv.Polygons(data=geography_pop, vdims=[vals, geo]).opts(colorbar=True, colorbar_position="right")).opts(axiswise=True, height=300, width=400, title=vals+" : "+str(grph_num), tools=["hover", ])#, colorbar=True, colorbar_position="right"
#                 grph_num+=1
#                 if adder==False: adder = curve
#                 else: adder+=curve
#                 print("time in choropleth :", time.time() -starting)
                geo = res[2]
                vals = res[5]
                #print("geo", (df.groupby(geo)))
                x=df.groupby(geo).mean()
                x.reset_index(inplace=True)
                if not flag:
                    if geo in ["states","state","States","State", "STATES", "STATE"]:
                        geography = gpd.read_file("lux/vislib/holoviews/us-states.json")
                        if isinstance(x[geo].iloc[0],numpy.int64):
                            left_name = "fips_num"
                            geography[left_name] = geography["id"].apply(lambda x: int(state_codes[x]))
                        geography_pop = geography.merge(x.to_pandas(), left_on=left_name, right_on=geo)
                    elif geo in ["Country", "COUNTRY", "country", "COUNTRIES","countries", "Countries"]:
                        geography = gpd.read_file("lux/vislib/holoviews/countries.geojson")
                        geography_pop = geography.merge(x.to_pandas(), left_on="ADMIN", right_on=geo)
                    flag =True
                if geo in ["states","state","States","State", "STATES", "STATE"]:
                    curve = hv.Polygons(data=geography_pop, vdims=[vals, geo]).opts(axiswise=True, xlim=(-170, -60), ylim=(10,75),  height=300, width=400, title=vals+" : "+str(grph_num), tools=["hover", ])#, colorbar=True, colorbar_position="right"
                elif geo in ["Country", "COUNTRY", "country", "COUNTRIES","countries", "Countries"]:
                    curve =  hv.Polygons(geography_pop, vdims=[vals, geo]).opts(colorbar=True, colorbar_position="right",axiswise=True, height=300, width=400, title=vals+" : "+str(grph_num), tools=["hover", ])#rasterize(hv.Polygons(data=data2, vdims=[vals, geo]).opts(colorbar=True, colorbar_position="right")).opts(axiswise=True, height=300, width=400, title=vals+" : "+str(grph_num), tools=["hover", ])#, colorbar=True, colorbar_position="right"
                grph_num+=1
                if adder==False: adder = curve
                else: adder+=curve
                #print("time in choropleth :", time.time() -starting)

    return hv.Layout(adder)