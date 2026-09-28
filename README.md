# ✈️ Flight Fuel & Emission Calculator

A research-informed aviation web application that estimates flight distance, fuel consumption, CO₂ emissions, operating fuel cost, and per-passenger environmental impact across international routes.

Built with **Python and Streamlit**, the project explores how aircraft selection and route distance can influence estimated fuel use and environmental impact. It developed alongside my research into aviation-emission modelling and sustainable aviation.

## 🌐 Live Application

**[Launch the Flight Fuel & Emission Calculator](https://flight-emissions-app-g4cgwpxcgribp68v5itqky.streamlit.app/)**

## 🔍 Project Overview

The application allows users to select an origin airport, destination airport, airline, and aircraft before generating model-based estimates for the selected flight.

Current project coverage includes:

- **31 international airports**
- **4 commercial airlines**
- **25+ aircraft**
- Route-distance calculations
- Aircraft-specific performance parameters
- Fuel-consumption estimation
- Total CO₂-emission estimation
- Per-passenger environmental impact
- Estimated fuel operating cost
- Aircraft range validation
- Aircraft comparison and visualisation

The project is designed as an **educational estimation and comparison tool**, rather than a certified airline operational or regulatory emissions model.

## 🧭 How It Works

### 1. Route Selection

The user selects an origin and destination airport. Airport coordinates and geodesic calculations are used to determine the approximate route distance.

### 2. Airline & Aircraft Selection

Users select an airline and one of the supported aircraft in its fleet. The aircraft database contains parameters including seating capacity, cruise speed, fuel burn, engine count, and operational range.

### 3. Flight Estimation

The application combines route and aircraft information to generate estimates for:

- Flight distance
- Fuel consumption
- Total CO₂ emissions
- CO₂ impact per passenger
- Estimated fuel cost

### 4. Aircraft Comparison

Supported aircraft can be compared on the same route to explore differences in estimated fuel consumption, emissions, and operating characteristics.

## 🧰 Technology Stack

| Area | Technology |
| --- | --- |
| Programming | Python |
| Web Application | Streamlit |
| Data Handling | Pandas |
| Visualisation | Altair |
| Geographic Calculations | geopy / geodesic |
| Version Control | Git & GitHub |
| Deployment | Streamlit Community Cloud |

## 📁 Project Structure

The application uses a modular structure that separates major datasets and application logic.

```text
flight-emissions-app/
├── app.py
├── aircraft.py
├── airports.py
├── airlines.py
├── requirements.txt
└── README.md
```

- `app.py` — main Streamlit application and calculation workflow
- `aircraft.py` — aircraft specifications and performance data
- `airports.py` — supported airport information and coordinates
- `airlines.py` — airline fleet information
- `requirements.txt` — Python dependencies

## 🔬 Research Background

This application developed alongside my research into aviation emissions and computational modelling through the **RISE Research Scholar Programme**.

I conducted ten weeks of research under one-on-one mentorship from **Yuiko Ichikawa**, who holds a **PhD in Meteorology from the University of Hokkaido** and an **MPhil in Data Intensive Science from the University of Cambridge**.

The research examined aviation-emission estimation, ICAO emissions factors, regression-based fuel-consumption approaches, and methodologies involving QAR, ADS-B, and simulated flight data. I initially explored a more complex AI-based approach, but limitations in accessible aviation datasets led me toward a more transparent regression-based framework.

The resulting research was published as:

### *Regression-Based Modeling of Flight Emissions and Per-Passenger Climate Impact*

**Muhammad Hadi — Sole Author**  
International Journal for Multidisciplinary Research (IJFMR)  
Volume 8, Issue 1, 2026

**[Read the Published Paper](https://www.ijfmr.com/research-paper.php?id=67871)**

The research helped inform the methodology and development of this application.

## ⚠️ Model Limitations

The calculator produces **model-based estimates** and should not be interpreted as exact operational flight data.

Actual aircraft fuel consumption and emissions can vary because of factors including:

- Payload and passenger load
- Weather and wind conditions
- Flight routing
- Altitude
- Aircraft and engine variant
- Taxi and ground operations
- Air traffic restrictions
- Airline operating procedures

Detailed airline operational data is not always publicly available, so the project uses accessible aircraft information, published aviation research, and modelling assumptions where necessary.

Recognising and communicating these limitations has been an important part of the project's development.

## 💻 Running the Application Locally

Clone the repository:

```bash
git clone https://github.com/muhammad7hadii/flight-emissions-app.git
cd flight-emissions-app
```

Create a virtual environment:

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

## 📈 Development

### Version 1.1 — July 2026

Major improvements included:

- Refactored the application into a modular structure by separating aircraft, airport, and airline data into dedicated Python modules.
- Expanded the aircraft database to 25+ commercial aircraft.
- Added airline-specific aircraft selection.
- Replaced fixed aircraft parameters with aircraft-specific calculations.
- Added aircraft specifications including manufacturer, category, seating capacity, cruise speed, range, engine count, and fuel burn.
- Implemented aircraft range validation to identify route-aircraft combinations that exceed the aircraft's modelled operating range.
- Added aircraft comparison functionality and data visualisation.
- Improved the application's structure to support future expansion.

## 🚧 Future Development

Potential future improvements include:

- Expanding the airport, airline, and aircraft databases
- Incorporating richer aircraft-performance datasets
- Improving flight-phase modelling
- Introducing a reliable aviation-fuel-price data source
- Adding uncertainty ranges and sensitivity analysis
- Improving aircraft and route comparison tools

## 👤 Author

**Muhammad Hadi**

- [Engineering Maker Portfolio](https://muhammad7hadii.github.io/hadi-maker-portfolio/)
- [LinkedIn](https://www.linkedin.com/in/muhammad-hadi-9a4661386/)
- [GitHub](https://github.com/muhammad7hadii)

---

*This project is an educational research and estimation tool and is not intended for operational flight planning or regulatory emissions reporting.*
   

