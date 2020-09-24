import pandas as pd
import numpy as np
def generate_scatter_data(numPoints):
    # Example from https://datashader.org/user_guide/Points.html
    from collections import OrderedDict as odict
    numPoints = int(numPoints/5)
    np.random.seed(1)

    dists = {cat: pd.DataFrame(odict([('x',np.random.normal(x,s,numPoints)), 
                                      ('y',np.random.normal(y,s,numPoints)), 
                                      ('val',val), 
                                      ('cat',cat)]))      
             for x,  y,  s,  val, cat in 
             [(  2,  2, 0.03, 10, "d1"), 
              (  2, -2, 0.10, 20, "d2"), 
              ( -2, -2, 0.50, 30, "d3"), 
              ( -2,  2, 1.00, 40, "d4"), 
              (  0,  0, 3.00, 50, "d5")] }

    df = pd.concat(dists,ignore_index=True)
    return df

def generate_airbnb_copies(ncopies):
    df = pd.read_csv("https://github.com/lux-org/lux-datasets/blob/master/data/airbnb_nyc.csv?raw=True")
    df = df[['id', 'name', 'host_id', 'host_name', 'neighbourhood_group',
       'neighbourhood', 'latitude', 'longitude', 'room_type', 'price',
       'minimum_nights', 'number_of_reviews']]
    df_copies = pd.concat([df for _x in range(ncopies)])
    return df_copies