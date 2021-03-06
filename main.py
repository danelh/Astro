import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy
from astropy.coordinates import get_sun, get_moon
from astropy.time import Time
import matplotlib.pyplot as plt

SYNODIC_MONTH = 29.530588
DATA_FOLDER = "data"

def arc_angle_to_decimal_angle(x):
    sign, d, m, s = x.signed_dms
    return sign*(((s+60*m) / 3600.0) + d)

def get_mean_elongation(start_time, duration_years, resulation_minutes=60):
    elongations = get_elongations(start_time, duration_years, resulation_minutes)
    # for us angle 350 is angle 10. becasue for mean eognation we want between 0 and 180
    elongations = [min(x, 360-x) for x in elongations]
    return numpy.average(elongations)

# returns array between 0 and 360
def get_elongations(start_time, duration_years, resulation_minutes=60):
    full_synodic_months_in_period = int((duration_years * 365.25) / SYNODIC_MONTH)
    total_seconds_in_period = full_synodic_months_in_period * SYNODIC_MONTH * 24 * 3600
    # start_timestamp = start_time.timestamp()
    start_timestamp = (start_time - datetime(1970, 1, 1)).total_seconds()

    measurement_dates = numpy.arange(start_timestamp,
                                    int(start_timestamp + total_seconds_in_period),
                                    resulation_minutes*60)
    times = Time(measurement_dates, format='unix')
    sun_locations = get_sun(times)
    sun_longitudes = sun_locations.geocentrictrueecliptic.lon
    moon_locations = get_moon(times)
    moon_longitudes = moon_locations.geocentrictrueecliptic.lon

    raw_elongations = moon_longitudes - sun_longitudes
    # elongations = [abs((arc_angle_to_decimal_angle(x) + 180) % 360 - 180) for x in raw_elongations]
    elongations = [arc_angle_to_decimal_angle(x) % 360 for x in raw_elongations]
    return elongations

def get_frequency_from_elongations(elongations):
    freq = [0] * 360
    for elongation in elongations:
        freq[round(elongation) % 360] += 1 # in case the angle is 360 we want 0

    return [float(x) / len(elongations) for x in freq]

def save_array(arr, file_name):
    txt = json.dumps(arr)
    f = open(file_name, mode="w+")
    f.write(txt)
    f.close()

def load_data():
    files = ["{}/{}".format(DATA_FOLDER, x) for x in os.listdir(DATA_FOLDER) if x.endswith(".txt")]
    freqs = []
    for file in files:
        f = open(file, mode="r")
        freqs.append(json.loads(f.read()))

    return freqs

def add_freqs(freqs):
    total_freq = [0] * 360
    for freq in freqs:
        for i in range(360):
            total_freq[i] += float(freq[i]) / len(freqs)

    return total_freq


def display_freq(freq):

    freq = [x - 1.0/len(freq) for x in freq]
    plt.bar(range(len(freq)), freq)
    plt.title('Elongation Frequency')
    plt.xlabel('Elongation')
    plt.ylabel('Frequency')
    plt.show()

def display_halves(freq):
    new_moon_half = freq[270:] + freq[:90] # 0 is in the middle
    full_moon_half = freq[90:270] # 180 in the middle


    diff = [new_moon_half[i] - full_moon_half[i] for i in range(180)]


    plt.bar(range(-90, 90), diff)
    plt.title('Elongation Frequency')
    plt.xlabel('Elongation')
    plt.ylabel('Frequency')
    plt.show()



def get_data():
    metonic_cycles_in_one_unit = 1
    minute_resolution = 20

    initial_time = datetime(year=1971, month=1, day=1)
    # randomly using Metonic cycle as our time unit. duration for each run.
    start_times = [initial_time + i*timedelta(days=SYNODIC_MONTH*235.0*metonic_cycles_in_one_unit) for i in range(100)]


    for start_time in start_times:
        print ("in time:{}".format(start_time))
        # mean_elongation_in_cycle = get_mean_elongation(start_time, 19.01*4, 400)
        # print (mean_elongation_in_cycle)
        file_name = "{}/{}_{}_{}.txt".format(DATA_FOLDER, start_time.strftime("%Y%m%d"),
                                           metonic_cycles_in_one_unit, minute_resolution)
        if Path(file_name).exists():
            print ("this file already exists. hence skip")
            continue
        cycle_elongation = get_elongations(start_time, 19.001*metonic_cycles_in_one_unit, minute_resolution)
        freq = get_frequency_from_elongations(cycle_elongation)
        save_array(freq, file_name)

# get_data()
# freqs = load_data()
# total_freq = add_freqs(freqs)
# display_freq(total_freq)
# display_halves(total_freq)
# display_freq(freqs[0])
# display_freq(freqs[1])