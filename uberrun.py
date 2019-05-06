import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import math
%matplotlib inline

# Prepare cluster dictionary
def get_coord(x):
    found = re.findall("\-?[0-9]+.[0-9]+", x)
    return((float(found[0]), float(found[1])))

cluster_dict = pd.read_csv("uber_clusterloc.csv?dl=0")
cluster_dict.drop(['Unnamed: 0'], axis = 1, inplace = True)
cluster_dict['Coord'] = cluster_dict['LatLon'].apply(lambda x: get_coord(x))

# Prepare Trips Data
trips = pd.read_csv("Uber_Test_GroundTruth.csv?dl=0")
trips['Time'] = trips['Hour'] * 60 + trips['Minute']
trips = pd.merge(trips, cluster_dict[['Cluster_Code', 'Coord']].rename(columns = {'Cluster_Code': 'Cluster_Start',
                                                                                 'Coord': 'Coord_Start'}),
                on = 'Cluster_Start')
trips = pd.merge(trips, cluster_dict[['Cluster_Code', 'Coord']].rename(columns = {'Cluster_Code': 'Cluster_End',
                                                                                 'Coord': 'Coord_End'}),
                on = 'Cluster_End')
trips.drop(['Hour', 'Minute', 'Cluster_Start', 'Cluster_End'], axis = 1, inplace = True)

# Prepare Prediction Data
BL = pd.read_csv("uber_prediction_v1.csv")
BL['Time'] = BL['Hour'] * 60 + BL['Minute'] * 15
BL = pd.merge(BL, cluster_dict[['Cluster_Code', 'Coord']].rename(columns = {'Cluster_Code': 'Cluster'}))
BL.drop(['Unnamed: 0', 'Hour', 'Minute', 'Cluster'], axis = 1, inplace = True)

# Prepare Oracle Prediction Data
oracleBL = trips.groupby(['Date', 'Time', 'Coord_Start']).size().reset_index().rename(columns = {0: 'P_Demand'})
oracleBL = pd.merge(oracleBL, trips.groupby(['Date', 'Time', 'Coord_Start'])['Trip Total'].mean().reset_index())
oracleBL.rename(columns = {'Coord_Start': 'Coord',
                          'Trip Total': 'P_Price'}, inplace = True)

##########
# RUN TEST
##########

from uber import find_reward, find_BL, find_travel_time
from uberdiag import test_loop, calc_total_revenue, test_shifts, plot_cum_revenue

cloc = (41.7815318023, -87.7716332109)
test_dates = list(BL['Date'].unique())

# Will save each of the dictionaries for the 11 different strategies
a,b,c,d,e,f,g,h,i,j,k = test_shifts(start_hour = 0, 
                                    shift_length = 24,
                                    start_location = cloc,
                                    trips = trips, 
                                    BL = BL,
                                    oracleBL = oracleBL,
                                    test_dates = test_dates)

# Plot the cumulative revenue across shift
plot_cum_revenue([a,b,c,d,e,f,g,h,i,j,k], 
                 ['baseline first', 'baseline random', 'oracle demand', 
                  'oracle price', 'oracle revenue',
                 'demand first', 'demand random', 'price first',
                 'price random', 'revenue first', 'revenue random'], test_dates)
