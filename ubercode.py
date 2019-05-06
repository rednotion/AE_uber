import numpy as np
import pandas as pd
from haversine import haversine
import matplotlib.pyplot as plt
from statistics import mean
import math
import random

def find_travel_time(current_location, next_location):
    right = next_location[1] >= current_location[1] #lat - y
    up = next_location[0] >= current_location[0] #long - x

    corner_long = max(next_location[1], current_location[1]) if right else min(next_location[1], current_location[1])
    corner_lat = min(current_location[0], next_location[0]) if up else max(current_location[0], next_location[0])
    corner = (corner_lat, corner_long)

    travel_distance = haversine(current_location, corner, unit = 'mi') + haversine(corner, next_location, unit = 'mi')

    speed = -1
    if speed < 0:
        speed = 10 + np.random.normal(5,5)

    return travel_distance / speed 

def find_BL(current_location, current_time, BL, optimizer):
    subset = BL[BL['Time'] >= current_time].reset_index(drop = True)
    
    if subset.shape[0] == 0:
        next_location = current_location
        travel_time = 1
    else:
        timerange = subset.iloc[0]['Time']
        subset = subset[subset['Time'] == timerange]

        clusters = list(subset['Coord'])
        demand = list(subset['P_Demand'])
        price = list(subset['P_Price'])
        distances = [find_travel_time(current_location, x) for x in clusters]

        if optimizer == 'demand':
            expected_reward = [i/(j+0.001) for i, j in zip(demand, distances)]
        elif optimizer == 'price':
            expected_reward = [i/(j+0.001) for i, j in zip(price, distances)]
        else:
            expected_reward = [(i*j)/(k+0.001) for i, j, k in zip(price, demand, distances)]

        BL_index = expected_reward.index(max(expected_reward))
        next_location = clusters[BL_index]

        if current_location == next_location:
            travel_time = 1
        else:
            travel_time = find_travel_time(current_location, next_location)

    return next_location, travel_time

def find_job(current_location, current_time, idle_time, strategy, data):
    subset = data[(data['Time'] >= current_time
        ) & (data['Time'] <= current_time + idle_time
        ) & (data['Coord_Start'] == current_location)].reset_index(drop = True)
    if subset.shape[0] > 0: 
        if strategy == 'first':
            entry = subset.iloc[0]
        elif strategy == 'oracle':
            subset['reward_by_distance'] = subset['Trip Total'] / subset['Trip Seconds']
            subset = subset.sort_values('reward_by_distance', ascending = False).reset_index(drop = True)
            entry = subset.iloc[0]
        else:
            entry = subset.iloc[random.randint(0, subset.shape[0]-1)]
        job_found = True
        job_location = entry['Coord_End'] # Final dest of job
        job_time = entry['Trip Seconds'] / 60
        job_reward = entry['Trip Total']
    else:
        job_found = False
        job_location = 0
        job_time = 0
        job_reward = 0
    return job_found, job_location, job_time, job_reward 

def find_reward(start_location, start_time, start_date, max_time, idle_time,
                BL_maximizer, strategy, 
                trips, BL, baseline = False, oracle = False):
    
    time = start_time
    max_time = start_time + max_time
    loc = start_location
    
    trips = trips[trips['Date'] == start_date]
    BL = BL[BL['Date'] == start_date]

    if oracle == True:
        strategy = 'oracle'

    reward = [0]
    time_log = [start_time]
    utilisation_log = [0]
    location_log = [start_location]

    while time <= max_time:
        job_found, job_loc, job_time, job_reward = find_job(loc, time, idle_time, strategy, trips)

        if job_found == True:
            time += math.ceil(job_time)
            loc = job_loc

            time_log.append(time)
            utilisation_log.append(1)
            location_log.append(loc)
            reward.append(job_reward)

        else:
            if baseline == False:
                next_loc, travel_time = find_BL(loc, time, BL, BL_maximizer)
                loc = next_loc
                time += math.ceil(travel_time)
            else:
                time += 1

            time_log.append(time)
            utilisation_log.append(0)
            location_log.append(loc)
            reward.append(0)
    
    return reward, time_log, utilisation_log, location_log
