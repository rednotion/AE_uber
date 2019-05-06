import numpy as np
import pandas as pd
from haversine import haversine
import matplotlib.pyplot as plt
from statistics import mean
import math
import random
from uber import find_reward, find_BL, find_travel_time

def test_loop(input_dict, start_hour, start_location, 
              shift_length, 
              BL_maximizer, strategy, 
              trips, BL, test_dates,
              baseline = False, oracle = False, 
              verbose = False):
    """
    Create an entry for every day in test_dates
    
    strategy : first, random
    """
    for date in test_dates:
        if verbose == True:
            print(date)
        r, t, u, l = find_reward(start_location = start_location,
                                 start_time = start_hour*60,
                                 start_date = date,
                                 max_time = shift_length*60,
                                 idle_time = 15,
                                 BL_maximizer = BL_maximizer,
                                 strategy = strategy,
                                 trips = trips,
                                 BL = BL,
                                 baseline = baseline,
                                 oracle = oracle)
        addrow = {'reward': r, 'time': t, 'utilisation': u,'location': l}
        input_dict[date] = addrow
        
    return input_dict

def calc_total_revenue(ref, name):
    rot_demand = dict()
    included_dates = list(ref.keys())
    for date in included_dates:
        for time, reward in zip(ref[date]['time'], ref[date]['reward']):
            if time not in rot_demand.keys():
                rot_demand[time] = reward
            else:
                rot_demand[time] += reward
    
    rot_demand_df = pd.DataFrame(data = {'time': list(rot_demand.keys()),
                                         'reward': list(rot_demand.values())}).sort_values('time')
    rot_demand_df['time'] = rot_demand_df['time']/60
    rot_demand_df['cum_reward'] = np.cumsum(rot_demand_df['reward']/len(included_dates))
    
    print("For", name, " = $", rot_demand_df['cum_reward'].max())

    
def test_shifts(start_hour, shift_length, start_location, trips, BL, oracleBL, test_dates):
    print(start_hour, "start,", shift_length, "hour shift")
    
    # Baseline First
    ref1 = dict()
    ref1 = test_loop(ref1, start_hour = start_hour, start_location = start_location,
                     shift_length = shift_length, 
              BL_maximizer = 'demand', strategy = 'first', 
              trips = trips, BL = BL, test_dates = test_dates,
              baseline = True, oracle = False, 
              verbose = False)
    calc_total_revenue(ref1, "Baseline First")
    
    # Baseline Random
    ref2 = dict()
    ref2 = test_loop(ref2, start_hour = start_hour, start_location = start_location,
                     shift_length = shift_length, 
              BL_maximizer = 'demand', strategy = 'random', 
              trips = trips, BL = BL, test_dates = test_dates,
              baseline = True, oracle = False, 
              verbose = False)
    calc_total_revenue(ref2, "Baseline Random")
    
    # Oracle Demand
    ref3 = dict()
    ref3 = test_loop(ref3, start_hour = start_hour, start_location = start_location,
                     shift_length = shift_length, 
              BL_maximizer = 'demand', strategy = 'oracle', 
              trips = trips, BL = BL, test_dates = test_dates,
              baseline = False, oracle = True, 
              verbose = False)
    calc_total_revenue(ref3, "Oracle Demand")
    
    # Oracle Price
    ref4 = dict()
    ref4 = test_loop(ref4, start_hour = start_hour, start_location = start_location,
                     shift_length = shift_length, 
              BL_maximizer = 'price', strategy = 'oracle', 
              trips = trips, BL = oracleBL, test_dates = test_dates,
              baseline = False, oracle = True, 
              verbose = False)
    calc_total_revenue(ref4, "Oracle Price")
    
    # Oracle Revenue
    ref5 = dict()
    ref5 = test_loop(ref5, start_hour = start_hour, start_location = start_location,
                     shift_length = shift_length, 
              BL_maximizer = 'revenue', strategy = 'oracle', 
              trips = trips, BL = oracleBL, test_dates = test_dates,
              baseline = False, oracle = True, 
              verbose = False)
    calc_total_revenue(ref5, "Oracle Revenue")
    
    # Demand First
    ref6 = dict()
    ref6 = test_loop(ref6, start_hour = start_hour, start_location = start_location,
                     shift_length = shift_length, 
              BL_maximizer = 'demand', strategy = 'first', 
              trips = trips, BL = BL, test_dates = test_dates,
              baseline = False, oracle = False, 
              verbose = False)
    calc_total_revenue(ref6, "Demand First")
    
    # Demand Random
    ref7 = dict()
    ref7 = test_loop(ref7, start_hour = start_hour, start_location = start_location,
                     shift_length = shift_length, 
              BL_maximizer = 'demand', strategy = 'random', 
              trips = trips, BL = BL, test_dates = test_dates,
              baseline = False, oracle = False, 
              verbose = False)
    calc_total_revenue(ref7, "Demand Random")
    
    # Price First
    ref8 = dict()
    ref8 = test_loop(ref8, start_hour = start_hour, start_location = start_location,
                     shift_length = shift_length, 
              BL_maximizer = 'price', strategy = 'first', 
              trips = trips, BL = BL, test_dates = test_dates,
              baseline = False, oracle = False, 
              verbose = False)
    calc_total_revenue(ref8, "Price First")
    
    # Price Random
    ref9 = dict()
    ref9 = test_loop(ref9, start_hour = start_hour, start_location = start_location,
                     shift_length = shift_length, 
              BL_maximizer = 'price', strategy = 'random', 
              trips = trips, BL = BL, test_dates = test_dates,
              baseline = False, oracle = False, 
              verbose = False)
    calc_total_revenue(ref9, "Price Random")
    
    # Revenue First
    ref10 = dict()
    ref10 = test_loop(ref10, start_hour = start_hour, start_location = start_location,
                      shift_length = shift_length, 
              BL_maximizer = 'revenue', strategy = 'first', 
              trips = trips, BL = BL, test_dates = test_dates,
              baseline = False, oracle = False, 
              verbose = False)
    calc_total_revenue(ref10, "Revenue First")
    
    # Revenue Random
    ref11 = dict()
    ref11 = test_loop(ref11, start_hour = start_hour, start_location = start_location,
                      shift_length = shift_length, 
              BL_maximizer = 'revenue', strategy = 'random', 
              trips = trips, BL = BL, test_dates = test_dates,
              baseline = False, oracle = False, 
              verbose = False)
    calc_total_revenue(ref11, "Revenue Random")
    
    return ref1, ref2, ref3, ref4, ref5, ref6, ref7, ref8, ref9, ref10, ref11


def plot_cum_revenue(input_list, name_list, test_dates):
    fig, ax = plt.subplots(figsize = (12, 4))
    for i, name in zip(input_list, name_list):
        rot_revenue = dict()
        for date in test_dates:
            for time, reward in zip(i[date]['time'], i[date]['reward']):
                if time not in rot_revenue.keys():
                    rot_revenue[time] = reward
                else:
                    rot_revenue[time] += reward
        rot_revenue_df = pd.DataFrame(data = {'time': list(rot_revenue.keys()),
                                              'reward': list(rot_revenue.values())}).sort_values('time')
        rot_revenue_df['time'] = rot_revenue_df['time']/60
        rot_revenue_df['cum_reward'] = np.cumsum(rot_revenue_df['reward']/len(test_dates))
    
        rot_revenue_df.plot(x = 'time', y = 'cum_reward', ax = ax, label = name)
    plt.title("Cumulative reward over hours")
    plt.xlabel("Shift hour")
    plt.ylabel("Cumulative $ earned")