from datetime import datetime, timedelta, timezone
import numpy
from astropy.coordinates import get_sun, get_moon
from astropy.time import Time

SYNODIC_MONTH = 29.530588

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


initial_time = datetime(year=1971, month=1, day=1)
# randomly using Metonic cycle as our time unit. duration for each run.
start_times = [initial_time + i*timedelta(days=SYNODIC_MONTH*235.0*4) for i in range(20)]


for start_time in start_times:
    mean_elongation_in_cycle = get_mean_elongation(start_time, 19.01*4, 400)
    print (mean_elongation_in_cycle)


