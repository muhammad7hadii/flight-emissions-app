"""
validation_helper.py

Helper for comparing the application with the official
ICAO Carbon Emissions Calculator.

HOW TO USE:

1. Run each route in the official ICAO calculator.
2. Use:
       One Way
       Economy
       1 passenger
3. Copy the ICAO CO2-per-passenger result into ICAO_RESULTS below.
4. Run:

       python validation_helper.py

5. Copy the printed Markdown table into README.md.
"""

from geopy.distance import geodesic

from aircraft import aircraft
from airports import airports
from calculations import calculate_flight_model


VALIDATION_CASES = [
    {
        "route": "LHE–KHI",
        "origin": "LHE - Lahore",
        "destination": "KHI - Karachi",
        "aircraft": "Airbus A320",
        "passengers": 144,
    },

    {
        "route": "LHR–CDG",
        "origin": "LHR - London Heathrow",
        "destination": "CDG - Paris Charles de Gaulle",
        "aircraft": "Airbus A320",
        "passengers": 144,
    },

    {
        "route": "LHE–DXB",
        "origin": "LHE - Lahore",
        "destination": "DXB - Dubai",
        "aircraft": "Boeing 777-300ER",
        "passengers": 317,
    },

    {
        "route": "LHR–JFK",
        "origin": "LHR - London Heathrow",
        "destination": "JFK - New York",
        "aircraft": "Boeing 787-9 Dreamliner",
        "passengers": 232,
    },

    {
        "route": "DXB–SYD",
        "origin": "DXB - Dubai",
        "destination": "SYD - Sydney",
        "aircraft": "Airbus A380-800",
        "passengers": 444,
    },
]


# -------------------------------------------------------------
# ENTER THE OFFICIAL ICAO RESULTS HERE
# -------------------------------------------------------------
#
# Example:
#
# "LHR–JFK": 350.2,
#
# DO NOT GUESS.
#
# Leave as None until you have run that route through the official
# ICAO Carbon Emissions Calculator.

ICAO_RESULTS = {
    "LHE–KHI": None,
    "LHR–CDG": None,
    "LHE–DXB": None,
    "LHR–JFK": None,
    "DXB–SYD": None,
}


def calculate_difference(app_value, icao_value):
    return (
        abs(app_value - icao_value)
        / icao_value
    ) * 100


print()
print(
    "| Route | Aircraft | App CO₂/Pax | "
    "ICAO CO₂/Pax | Difference |"
)

print(
    "|---|---|---:|---:|---:|"
)


for case in VALIDATION_CASES:

    ac = aircraft[
        case["aircraft"]
    ]

    distance_km = geodesic(
        airports[
            case["origin"]
        ],

        airports[
            case["destination"]
        ],
    ).km


    result = calculate_flight_model(
        great_circle_distance_km=
            distance_km,

        cruise_speed_kmh=
            ac["cruise_speed"],

        reference_fuel_burn_kg_h=
            ac["fuel_burn_kg_h"],

        passengers=
            case["passengers"],

        fuel_price_per_liter=
            0.92,
    )


    app_value = (
        result[
            "co2_per_passenger_kg"
        ]
    )


    icao_value = (
        ICAO_RESULTS[
            case["route"]
        ]
    )


    if icao_value is None:

        icao_text = "PENDING"
        difference_text = "PENDING"

    else:

        difference = calculate_difference(
            app_value,
            icao_value,
        )

        icao_text = (
            f"{icao_value:.1f} kg"
        )

        difference_text = (
            f"{difference:.1f}%"
        )


    print(
        f"| {case['route']} "
        f"| {case['aircraft']} "
        f"| {app_value:.1f} kg "
        f"| {icao_text} "
        f"| {difference_text} |"
    )


print()

if any(
    value is None
    for value in ICAO_RESULTS.values()
):

    print(
        "WARNING: ICAO validation is incomplete. "
        "Do not describe the five-route validation as complete "
        "until every PENDING value has been replaced."
    )
