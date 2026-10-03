import streamlit as st
import altair as alt
import pandas as pd

from geopy.distance import geodesic

from aircraft import aircraft
from airports import airports
from airlines import airlines

from calculations import (
    CO2_KG_PER_KG_FUEL,
    DISTANCE_CORRECTION_FACTOR,
    JET_FUEL_DENSITY_KG_PER_LITER,
    LTO_TIMES_MIN,
    calculate_flight_model,
)


# -------------------------------------------------------------
# PAGE SETUP
# -------------------------------------------------------------

st.set_page_config(
    page_title="Flight Fuel & Emission Calculator",
    page_icon="✈️",
    layout="wide",
)

st.title("✈️ Flight Fuel & Emission Calculator")

st.caption(
    f"Database coverage: "
    f"{len(airports)} airports • "
    f"{len(airlines)} airlines • "
    f"{len(aircraft)} aircraft"
)

st.info(
    "Methodology v2 applies the published 1.099 route-distance "
    "correction, ICAO LTO time-in-mode values, CCD cruise-time "
    "equations, corrected fuel-unit handling, and CO₂-per-passenger "
    "output."
)


# -------------------------------------------------------------
# ROUTE INPUTS
# -------------------------------------------------------------

origin = st.selectbox(
    "Select origin airport",
    list(airports.keys()),
)

destination = st.selectbox(
    "Select destination airport",
    list(airports.keys()),
    index=1,
)


# -------------------------------------------------------------
# AIRCRAFT SELECTION
# -------------------------------------------------------------

selection_mode = st.radio(
    "Aircraft selection",
    [
        "Browse all aircraft",
        "Filter by airline",
    ],
    horizontal=True,
)


if selection_mode == "Browse all aircraft":

    all_aircraft = list(
        aircraft.keys()
    )

    aircraft1 = st.selectbox(
        "✈️ First aircraft",
        all_aircraft,
        index=3,
        key="all_ac1",
    )

    aircraft2 = st.selectbox(
        "✈️ Second aircraft",
        all_aircraft,
        index=11,
        key="all_ac2",
    )

    airline1 = None
    airline2 = None


else:

    airline1 = st.selectbox(
        "🏢 Select first airline",
        list(airlines.keys()),
        key="air1",
    )

    aircraft1 = st.selectbox(
        "✈️ First aircraft",
        airlines[airline1],
        key="airline_ac1",
    )

    airline2 = st.selectbox(
        "🏢 Select second airline",
        list(airlines.keys()),
        index=1,
        key="air2",
    )

    aircraft2 = st.selectbox(
        "✈️ Second aircraft",
        airlines[airline2],
        key="airline_ac2",
    )


# -------------------------------------------------------------
# PASSENGERS
# -------------------------------------------------------------

max_capacity = max(
    data["seats"]
    for data in aircraft.values()
)

passengers = st.slider(
    "Number of passengers",
    min_value=1,
    max_value=max_capacity,
    value=150,
)


# -------------------------------------------------------------
# FUEL PRICE
# -------------------------------------------------------------

fuel_price_per_liter = st.number_input(
    "Assumed jet-fuel price (USD per litre)",
    min_value=0.0,
    max_value=5.0,
    value=0.92,
    step=0.01,
)

st.caption(
    f"Fuel price is a user-adjustable assumption, not a live "
    f"market feed. Fuel mass is converted to approximate volume "
    f"using {JET_FUEL_DENSITY_KG_PER_LITER:.2f} kg/L."
)


# -------------------------------------------------------------
# CALCULATION
# -------------------------------------------------------------

if st.button(
    "Calculate",
    type="primary",
):

    # ---------------------------------------------------------
    # SAME-AIRPORT CHECK
    # ---------------------------------------------------------

    if origin == destination:

        st.error(
            "Origin and destination airports must be different."
        )

        st.stop()


    # ---------------------------------------------------------
    # GREAT-CIRCLE DISTANCE
    # ---------------------------------------------------------

    great_circle_distance_km = geodesic(
        airports[origin],
        airports[destination],
    ).km


    corrected_route_distance = (
        great_circle_distance_km
        * DISTANCE_CORRECTION_FACTOR
    )


    st.subheader("Route")

    route_col1, route_col2 = st.columns(2)

    route_col1.metric(
        "Great-circle distance",
        f"{great_circle_distance_km:,.1f} km",
    )

    route_col2.metric(
        f"Corrected distance "
        f"(× {DISTANCE_CORRECTION_FACTOR})",
        f"{corrected_route_distance:,.1f} km",
    )


    # Prevent duplicate dictionary entries if both aircraft are same.
    selected_aircraft = list(
        dict.fromkeys(
            [
                aircraft1,
                aircraft2,
            ]
        )
    )


    if len(selected_aircraft) == 1:

        st.warning(
            "You selected the same aircraft twice, so it will "
            "be calculated once."
        )


    results = {}


    # ---------------------------------------------------------
    # PROCESS EACH AIRCRAFT
    # ---------------------------------------------------------

    for ac in selected_aircraft:

        data = aircraft[ac]

        capacity = data["seats"]


        st.divider()

        st.subheader(
            f"Results for {ac}"
        )


        # -----------------------------------------------------
        # RANGE CHECK
        # -----------------------------------------------------

        if corrected_route_distance > data["range"]:

            st.error(
                f"{ac} is outside the modelled range for this "
                f"route.\n\n"
                f"Corrected route distance: "
                f"{corrected_route_distance:,.0f} km\n\n"
                f"Listed aircraft range: "
                f"{data['range']:,} km"
            )

            continue


        # -----------------------------------------------------
        # PASSENGER CAPACITY CHECK
        # -----------------------------------------------------

        if passengers > capacity:

            st.error(
                f"{passengers} passengers exceeds the listed "
                f"typical capacity of {capacity} for {ac}. "
                f"Reduce the passenger count to include this "
                f"aircraft in the comparison."
            )

            continue


        # -----------------------------------------------------
        # RUN MODEL
        # -----------------------------------------------------

        result = calculate_flight_model(
            great_circle_distance_km=
                great_circle_distance_km,

            cruise_speed_kmh=
                data["cruise_speed"],

            reference_fuel_burn_kg_h=
                data["fuel_burn_kg_h"],

            passengers=
                passengers,

            fuel_price_per_liter=
                fuel_price_per_liter,
        )


        results[ac] = result


        # -----------------------------------------------------
        # HEADLINE OUTPUTS
        # -----------------------------------------------------

        metric1, metric2, metric3 = st.columns(3)


        metric1.metric(
            "Estimated total fuel",
            f"{result['total_fuel_kg']:,.0f} kg",
        )


        metric2.metric(
            "Estimated total CO₂",
            f"{result['total_co2_kg']:,.0f} kg",
        )


        metric3.metric(
            "CO₂ per passenger",
            f"{result['co2_per_passenger_kg']:,.1f} kg",
        )


        # -----------------------------------------------------
        # SECONDARY COST INFORMATION
        # -----------------------------------------------------

        st.write(
            f"Approximate fuel volume: "
            f"**{result['fuel_volume_liters']:,.0f} L**"
        )


        st.write(
            f"Estimated fuel cost: "
            f"**${result['fuel_cost_usd']:,.2f}**"
        )


        st.write(
            f"Estimated fuel cost per passenger: "
            f"**${result['fuel_cost_per_passenger_usd']:,.2f}**"
        )


        # -----------------------------------------------------
        # METHODOLOGY DETAILS
        # -----------------------------------------------------

        with st.expander(
            "Methodology and phase breakdown"
        ):

            st.write(
                f"**Reference fuel burn:** "
                f"{data['fuel_burn_kg_h']:,} kg/h"
            )


            st.write(
                f"**ICAO LTO duration:** "
                f"{result['lto_time_min']:.1f} min"
            )


            st.write(
                f"- Idle: "
                f"{LTO_TIMES_MIN['idle']} min"
            )

            st.write(
                f"- Approach: "
                f"{LTO_TIMES_MIN['approach']} min"
            )

            st.write(
                f"- Climb-out: "
                f"{LTO_TIMES_MIN['climb_out']} min"
            )

            st.write(
                f"- Take-off: "
                f"{LTO_TIMES_MIN['takeoff']} min"
            )


            st.write(
                f"**CCD duration:** "
                f"{result['ccd_time_min']:.1f} min"
            )


            st.write(
                f"**CCD climb / cruise / descent:** "
                f"{result['climb_time_min']:.1f} / "
                f"{result['cruise_time_min']:.1f} / "
                f"{result['descent_time_min']:.1f} min"
            )


            st.write(
                f"**LTO fuel:** "
                f"{result['lto_fuel_kg']:,.0f} kg"
            )


            st.write(
                f"**CCD fuel:** "
                f"{result['ccd_fuel_kg']:,.0f} kg"
            )


            st.write(
                f"**CO₂ factor:** "
                f"{CO2_KG_PER_KG_FUEL:.3f} "
                f"kg CO₂ per kg fuel"
            )


            phase_rows = []


            for phase, fuel_kg in (
                result["lto_phase_fuel_kg"].items()
            ):

                phase_rows.append(
                    {
                        "Cycle": "LTO",
                        "Phase":
                            phase.replace(
                                "_",
                                " ",
                            ).title(),

                        "Fuel (kg)":
                            fuel_kg,
                    }
                )


            for phase, fuel_kg in (
                result["ccd_phase_fuel_kg"].items()
            ):

                phase_rows.append(
                    {
                        "Cycle": "CCD",
                        "Phase":
                            phase.title(),

                        "Fuel (kg)":
                            fuel_kg,
                    }
                )


            phase_df = pd.DataFrame(
                phase_rows
            )


            st.dataframe(
                phase_df.style.format(
                    {
                        "Fuel (kg)":
                            "{:,.1f}"
                    }
                ),

                use_container_width=True,
                hide_index=True,
            )


        # -----------------------------------------------------
        # AIRCRAFT SPECIFICATIONS
        # -----------------------------------------------------

        with st.expander(
            f"{ac} specifications"
        ):

            st.write(
                f"**Manufacturer:** "
                f"{data['manufacturer']}"
            )

            st.write(
                f"**Category:** "
                f"{data['category']}"
            )

            st.write(
                f"**Typical seats:** "
                f"{data['seats']}"
            )

            st.write(
                f"**Cruise speed:** "
                f"{data['cruise_speed']} km/h"
            )

            st.write(
                f"**Listed range:** "
                f"{data['range']:,} km"
            )

            st.write(
                f"**Engines:** "
                f"{data['engines']}"
            )

            st.write(
                f"**Reference fuel burn:** "
                f"{data['fuel_burn_kg_h']:,} kg/h"
            )


    # ---------------------------------------------------------
    # COMPARISON
    # ---------------------------------------------------------

    if results:

        st.divider()

        st.subheader(
            "Aircraft comparison"
        )


        comparison_data = pd.DataFrame(
            [
                {
                    "Aircraft":
                        name,

                    "CO₂ per passenger (kg)":
                        values[
                            "co2_per_passenger_kg"
                        ],

                    "Total fuel (kg)":
                        values[
                            "total_fuel_kg"
                        ],
                }

                for name, values
                in results.items()
            ]
        )


        # CO2 chart

        co2_chart = (
            alt.Chart(
                comparison_data
            )
            .mark_bar()
            .encode(
                x=alt.X(
                    "Aircraft:N",
                    sort=None,
                ),

                y=alt.Y(
                    "CO₂ per passenger (kg):Q"
                ),

                tooltip=[
                    "Aircraft:N",

                    alt.Tooltip(
                        "CO₂ per passenger (kg):Q",
                        format=",.1f",
                    ),
                ],
            )
            .properties(
                title=
                    "Modelled CO₂ per passenger"
            )
        )


        st.altair_chart(
            co2_chart,
            use_container_width=True,
        )


        # Fuel chart

        fuel_chart = (
            alt.Chart(
                comparison_data
            )
            .mark_bar()
            .encode(
                x=alt.X(
                    "Aircraft:N",
                    sort=None,
                ),

                y=alt.Y(
                    "Total fuel (kg):Q"
                ),

                tooltip=[
                    "Aircraft:N",

                    alt.Tooltip(
                        "Total fuel (kg):Q",
                        format=",.0f",
                    ),
                ],
            )
            .properties(
                title=
                    "Modelled total fuel use"
            )
        )


        st.altair_chart(
            fuel_chart,
            use_container_width=True,
        )


        # -----------------------------------------------------
        # COMPARATIVE RESULT
        # -----------------------------------------------------

        if len(results) >= 2:

            lower_name = min(
                results,

                key=lambda name:
                    results[name][
                        "co2_per_passenger_kg"
                    ],
            )


            higher_name = max(
                results,

                key=lambda name:
                    results[name][
                        "co2_per_passenger_kg"
                    ],
            )


            lower_value = (
                results[lower_name][
                    "co2_per_passenger_kg"
                ]
            )


            higher_value = (
                results[higher_name][
                    "co2_per_passenger_kg"
                ]
            )


            difference = (
                higher_value
                - lower_value
            )


            percent_difference = (
                (
                    difference
                    / higher_value
                )
                * 100

                if higher_value > 0
                else 0.0
            )


            st.success(
                f"For the selected passenger count, "
                f"{lower_name} has "
                f"{difference:,.1f} kg less modelled "
                f"CO₂ per passenger "
                f"({percent_difference:.1f}% lower) "
                f"than {higher_name}."
            )


    # ---------------------------------------------------------
    # LIMITATION
    # ---------------------------------------------------------

    st.caption(
        "This is an educational first-order estimation model. "
        "Actual aircraft fuel consumption depends on payload, "
        "weather, routing, engine variant, altitude, taxi time, "
        "airline operating procedures, and other operational "
        "conditions."
    )
