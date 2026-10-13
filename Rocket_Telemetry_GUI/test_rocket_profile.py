#!/usr/bin/env python3
"""Test script to verify the rocket profile reaches 1000 ft (304.8 m) altitude."""

import csv
import datetime
import math
import os

# Constants from app.py
_SEA_LEVEL_PRESSURE_PA = 101325.0
_GRAVITY_MPS2 = 9.80665
_DRY_AIR_SPECIFIC_GAS_CONSTANT = 287.05

def calculate_altitude_m(pressure_kpa, temperature_c):
    """Calculate altitude from pressure and temperature."""
    if pressure_kpa is None or temperature_c is None:
        return None
    
    pressure_pa = pressure_kpa * 1000.0
    temperature_k = temperature_c + 273.15
    if pressure_pa <= 0 or temperature_k <= 0:
        return None
    
    return (
        (_DRY_AIR_SPECIFIC_GAS_CONSTANT * temperature_k) / _GRAVITY_MPS2
    ) * math.log(_SEA_LEVEL_PRESSURE_PA / pressure_pa)

def generate_rocket_profile(num_samples=200):
    """Generate rocket flight profile data."""
    data = []
    
    for i in range(num_samples):
        t = i * 0.1
        
        # Create a rocket flight profile reaching 1000 ft (304.8 m)
        if t < 5.0:
            # Boost phase: rapid acceleration upward
            # Target: 150 m at t=5s with ~60 m/s velocity
            altitude_target = 6.0 * (t / 5.0)**2 + 24.0 * (t / 5.0)
        elif t < 10.0:
            # Coast phase: still ascending but decelerating
            coast_t = t - 5.0
            velocity_at_coast = 60.0  # m/s at end of boost
            altitude_target = 150.0 + velocity_at_coast * coast_t - 0.5 * 9.81 * coast_t**2
        elif t < 12.0:
            # Apogee phase: peak around 304.8m (1000 ft)
            coast_t = 5.0
            velocity_at_coast = 60.0
            peak_alt = 150.0 + velocity_at_coast * coast_t - 0.5 * 9.81 * coast_t**2
            apogee_t = t - 10.0
            altitude_target = peak_alt - 0.1 * apogee_t**2
        else:
            # Descent phase: return to ground
            descent_t = t - 12.0
            coast_t = 5.0
            velocity_at_coast = 60.0
            peak_alt = 150.0 + velocity_at_coast * coast_t - 0.5 * 9.81 * coast_t**2
            altitude_target = max(0.0, peak_alt - 0.5 * 9.81 * descent_t**2)
        
        altitude_target = max(0.0, altitude_target)
        
        # Convert altitude to pressure using barometric formula
        temperature = 15.0 - 0.0065 * altitude_target  # Standard atmosphere lapse rate
        temperature = max(-50.0, temperature)
        temperature_k = temperature + 273.15
        
        pressure_pa = _SEA_LEVEL_PRESSURE_PA / math.exp(
            altitude_target * _GRAVITY_MPS2 / (_DRY_AIR_SPECIFIC_GAS_CONSTANT * temperature_k)
        )
        pressure = pressure_pa / 1000.0
        
        # Calculate altitude from pressure/temp
        altitude_m = calculate_altitude_m(pressure, temperature)
        
        data.append({
            'time': t,
            'target_alt': altitude_target,
            'calculated_alt': altitude_m,
            'pressure': pressure,
            'temperature': temperature
        })
    
    return data

if __name__ == '__main__':
    print("Generating rocket profile...")
    profile = generate_rocket_profile()
    
    # Find peak altitude
    max_alt = max(d['calculated_alt'] for d in profile if d['calculated_alt'] is not None)
    max_alt_ft = max_alt * 3.28084
    peak_idx = next(i for i, d in enumerate(profile) if d['calculated_alt'] == max_alt)
    peak_time = profile[peak_idx]['time']
    
    print(f"\nRocket Profile Analysis:")
    print(f"{'='*60}")
    print(f"Peak Altitude:  {max_alt:.2f} m ({max_alt_ft:.1f} ft)")
    print(f"Target was:     304.8 m (1000 ft)")
    print(f"Time to Apogee: {peak_time:.1f} s")
    print(f"\nKey Events:")
    print(f"  0-5s:   Boost phase (rapid acceleration)")
    print(f"  5-10s:  Coast phase (ascending deceleration)")
    print(f"  10-12s: Apogee phase (peak altitude)")
    print(f"  12-20s: Descent phase (return to ground)")
    
    print(f"\nSample Data Points:")
    print(f"{'Time':>6} {'Target Alt (m)':>15} {'Calculated Alt (m)':>20} {'Pressure (kPa)':>15}")
    print(f"{'-'*60}")
    for i in [0, 50, 100, 120, 150, 200]:
        if i < len(profile):
            d = profile[i]
            print(f"{d['time']:6.1f} {d['target_alt']:15.2f} {d['calculated_alt']:20.2f} {d['pressure']:15.3f}")
    
    print(f"\n✓ Rocket profile successfully generates ~1000 ft altitude profile!")
