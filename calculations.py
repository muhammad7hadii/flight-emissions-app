"""
calculations.py

Core methodology for the Flight Fuel & Emission Calculator.

Implements the explicit components described in the published paper:

- 1.099 great-circle distance correction
- ICAO LTO time-in-mode values
- LTO / CCD segmentation
- published piecewise CCD cruise-duration equations
- correction-factor structure for phase fuel flow
- 3.149 kg CO2 per kg fuel
- CO2 per passenger

Published paper:
Muhammad Hadi (2026)
"Regression-Based Modeling of Flight Emissions and
Per-Passenger Climate Impact"
IJFMR, Volume 8, Issue 1.

Important implementation note
-----------------------------
The published paper does not provide a complete numerical table of
aircraft-specific FF0 values or regression intercepts for all 25 aircraft
included in the current application.

The current implementation therefore:

1. Uses the aircraft reference fuel-burn value in aircraft.py as the
   aircraft-level regression slope for total CCD fuel, with a zero
   intercept.

2. Uses transparent normalized phase weights only to distribute the
   already-computed total CCD fuel across climb/cruise/descent.

3. Uses the fuel-flow correction-factor equation so the distributed
   phase fuel totals always sum back to F_CCD.

These normalized weights are NOT presented as engine-specific ICAO EEDB
measurements.
"""

DISTANCE_CORRECTION_FACTOR = 1.099

CO2_KG_PER_KG_FUEL = 3.149

# Used only when converting fuel mass to approximate volume for cost.
JET_FUEL_DENSITY_KG_PER_LITER = 0.80


# ICAO standard LTO time-in-mode values, in minutes.
LTO_TIMES_MIN = {
    "idle": 26.0,
    "approach": 4.0,
    "climb_out": 2.2,
    "takeoff": 0.7,
}


# Standard ICAO certification thrust settings.
#
# Here they are used only as normalized reference weights to distribute
# the aircraft-level LTO fuel estimate across the four LTO phases.
# They are NOT treated as direct fuel-flow measurements.
LTO_REFERENCE_RATIOS = {
    "idle": 0.07,
    "approach": 0.30,
    "climb_out": 0.85,
    "takeoff": 1.00,
}


# Normalized reference profile for distributing the CCD total.
#
# The correction factor later rescales these values so that:
#
# sum(phase fuel) = F_CCD
#
# These are normalized modelling weights rather than claimed
# aircraft-engine-specific EEDB measurements.
CCD_REFERENCE_RATIOS = {
    "climb": 0.85,
    "cruise": 0.30,
    "descent": 0.07,
}


def corrected_distance_km(great_circle_distance_km):
    """
    Apply the +9.9% distance correction described in the paper.
    """

    if great_circle_distance_km < 0:
        raise ValueError("Distance cannot be negative.")

    return great_circle_distance_km * DISTANCE_CORRECTION_FACTOR


def cruise_time_minutes(ccd_time_minutes):
    """
    Calculate CCD cruise duration using the three piecewise equations
    stated in the published Methodology section.

    Short haul (<60 min):
        t_CR = -4.7 + 0.33t'

    Medium haul (60-120 min):
        t_CR = -42 + 0.97t'

    Long haul (>120 min):
        t_CR = -48 + 0.99t'
    """

    if ccd_time_minutes < 0:
        raise ValueError("CCD time cannot be negative.")

    if ccd_time_minutes < 60:
        cruise = -4.7 + (0.33 * ccd_time_minutes)

    elif ccd_time_minutes <= 120:
        cruise = -42 + (0.97 * ccd_time_minutes)

    else:
        cruise = -48 + (0.99 * ccd_time_minutes)

    # Prevent impossible negative cruise time or cruise time greater
    # than the complete CCD duration.
    return max(0.0, min(cruise, ccd_time_minutes))


def ccd_phase_durations(ccd_time_minutes):
    """
    Determine climb, cruise and descent durations.

    The paper publishes the cruise-time equations but does not provide
    a separate numerical rule for dividing the remaining non-cruise
    CCD duration between climb and descent.

    Therefore, the remaining duration is divided equally between climb
    and descent as an explicit implementation assumption.
    """

    cruise = cruise_time_minutes(ccd_time_minutes)

    non_cruise_time = max(
        0.0,
        ccd_time_minutes - cruise,
    )

    return {
        "climb": non_cruise_time / 2.0,
        "cruise": cruise,
        "descent": non_cruise_time / 2.0,
    }


def _distribute_total_fuel(
    total_fuel_kg,
    durations_min,
    reference_flows_kg_h,
):
    """
    Apply the fuel-flow correction structure from the paper.

    f_FF = F_total /
           sum(FF0_phase * phase_duration)

    adjusted_FF_phase = f_FF * FF0_phase

    This guarantees that the sum of the phase fuel quantities equals
    the already-estimated total fuel quantity.
    """

    denominator_kg = sum(
        reference_flows_kg_h[phase]
        * (minutes / 60.0)
        for phase, minutes in durations_min.items()
    )

    if denominator_kg <= 0:
        adjusted_flows = {
            phase: 0.0
            for phase in durations_min
        }

        phase_fuel = {
            phase: 0.0
            for phase in durations_min
        }

        return 0.0, adjusted_flows, phase_fuel

    correction_factor = (
        total_fuel_kg / denominator_kg
    )

    adjusted_flows = {
        phase:
        reference_flows_kg_h[phase]
        * correction_factor
        for phase in durations_min
    }

    phase_fuel = {
        phase:
        adjusted_flows[phase]
        * (minutes / 60.0)
        for phase, minutes in durations_min.items()
    }

    return (
        correction_factor,
        adjusted_flows,
        phase_fuel,
    )


def calculate_flight_model(
    great_circle_distance_km,
    cruise_speed_kmh,
    reference_fuel_burn_kg_h,
    passengers,
    fuel_price_per_liter=0.92,
):
    """
    Run the complete model for one aircraft and route.
    """

    if cruise_speed_kmh <= 0:
        raise ValueError(
            "Cruise speed must be greater than zero."
        )

    if reference_fuel_burn_kg_h <= 0:
        raise ValueError(
            "Reference fuel burn must be greater than zero."
        )

    if passengers <= 0:
        raise ValueError(
            "Passenger count must be greater than zero."
        )

    if fuel_price_per_liter < 0:
        raise ValueError(
            "Fuel price cannot be negative."
        )

    # ---------------------------------------------------------
    # 1. Great-circle distance correction
    # ---------------------------------------------------------

    corrected_km = corrected_distance_km(
        great_circle_distance_km
    )

    # ---------------------------------------------------------
    # 2. CCD duration
    # ---------------------------------------------------------
    #
    # Route distance / cruise speed provides a reproducible
    # aircraft-specific approximation for time above the LTO zone.

    ccd_time_min = (
        corrected_km / cruise_speed_kmh
    ) * 60.0

    ccd_durations = ccd_phase_durations(
        ccd_time_min
    )

    # ---------------------------------------------------------
    # 3. CCD fuel
    # ---------------------------------------------------------
    #
    # Linear form:
    #
    # F_CCD = a * T_CCD + b
    #
    # Current aircraft reference burn is used as slope a,
    # expressed in kg/min.
    #
    # b = 0 because the published paper does not contain a
    # complete 25-aircraft intercept table.

    ccd_fuel_kg = (
        reference_fuel_burn_kg_h / 60.0
    ) * ccd_time_min

    ccd_reference_flows = {
        phase:
        reference_fuel_burn_kg_h * ratio

        for phase, ratio
        in CCD_REFERENCE_RATIOS.items()
    }

    (
        ccd_correction_factor,
        ccd_adjusted_flows,
        ccd_phase_fuel,
    ) = _distribute_total_fuel(
        ccd_fuel_kg,
        ccd_durations,
        ccd_reference_flows,
    )

    # ---------------------------------------------------------
    # 4. LTO cycle
    # ---------------------------------------------------------

    lto_total_time_min = sum(
        LTO_TIMES_MIN.values()
    )

    lto_fuel_kg = (
        reference_fuel_burn_kg_h / 60.0
    ) * lto_total_time_min

    lto_reference_flows = {
        phase:
        reference_fuel_burn_kg_h * ratio

        for phase, ratio
        in LTO_REFERENCE_RATIOS.items()
    }

    (
        lto_correction_factor,
        lto_adjusted_flows,
        lto_phase_fuel,
    ) = _distribute_total_fuel(
        lto_fuel_kg,
        LTO_TIMES_MIN,
        lto_reference_flows,
    )

    # ---------------------------------------------------------
    # 5. Total fuel and emissions
    # ---------------------------------------------------------

    total_fuel_kg = (
        ccd_fuel_kg + lto_fuel_kg
    )

    total_co2_kg = (
        total_fuel_kg
        * CO2_KG_PER_KG_FUEL
    )

    co2_per_passenger_kg = (
        total_co2_kg / passengers
    )

    # ---------------------------------------------------------
    # 6. Mass -> volume conversion for COST ONLY
    # ---------------------------------------------------------

    fuel_volume_liters = (
        total_fuel_kg
        / JET_FUEL_DENSITY_KG_PER_LITER
    )

    fuel_cost_usd = (
        fuel_volume_liters
        * fuel_price_per_liter
    )

    fuel_cost_per_passenger_usd = (
        fuel_cost_usd / passengers
    )

    return {
        "great_circle_distance_km":
            great_circle_distance_km,

        "corrected_distance_km":
            corrected_km,

        "lto_time_min":
            lto_total_time_min,

        "ccd_time_min":
            ccd_time_min,

        "total_model_time_min":
            lto_total_time_min + ccd_time_min,

        "cruise_time_min":
            ccd_durations["cruise"],

        "climb_time_min":
            ccd_durations["climb"],

        "descent_time_min":
            ccd_durations["descent"],

        "lto_fuel_kg":
            lto_fuel_kg,

        "ccd_fuel_kg":
            ccd_fuel_kg,

        "total_fuel_kg":
            total_fuel_kg,

        "total_co2_kg":
            total_co2_kg,

        "co2_per_passenger_kg":
            co2_per_passenger_kg,

        "fuel_volume_liters":
            fuel_volume_liters,

        "fuel_cost_usd":
            fuel_cost_usd,

        "fuel_cost_per_passenger_usd":
            fuel_cost_per_passenger_usd,

        "ccd_correction_factor":
            ccd_correction_factor,

        "lto_correction_factor":
            lto_correction_factor,

        "ccd_adjusted_flows_kg_h":
            ccd_adjusted_flows,

        "lto_adjusted_flows_kg_h":
            lto_adjusted_flows,

        "ccd_phase_fuel_kg":
            ccd_phase_fuel,

        "lto_phase_fuel_kg":
            lto_phase_fuel,
    }
