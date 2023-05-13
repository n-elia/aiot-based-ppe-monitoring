"""Helpers for RSSI-related computations."""

from math import pow

MEASURED_POWER = -60  # RSSI @1m distance
ENVIRONM_FACTOR = 2  # Environmental factor. Spans from 2 to 4.


def compute_distance_m(rssi_value):
    """!
    Estimate the distance leveraging the RSSI value.
    Return a float number representing the distance in meter.
    
    rssi_value: RSSI value to convert in distance.
    """
    return pow(10, (MEASURED_POWER-rssi_value)/(10*ENVIRONM_FACTOR))
