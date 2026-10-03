# ✈️ Flight Fuel & Emission Calculator

A research-informed aviation web application for estimating flight distance, aircraft fuel consumption, total CO₂ emissions, and per-passenger CO₂ impact across international routes.

The application was developed alongside my research into aviation-emission modelling and sustainable aviation.

## 🌐 Live Application

**[Launch the Flight Fuel & Emission Calculator](https://flight-emissions-app-g4cgwpxcgribp68v5itqky.streamlit.app/)**

> The live application is deployed from the stable `main` branch. Methodological changes are developed and tested separately before being merged into production.

---

## 🔍 Current Project Coverage

The current database contains:

- **31 international airports**
- **4 commercial airline filters**
- **25 aircraft**
- Great-circle route calculations
- +9.9% route-distance correction
- LTO and CCD flight-phase modelling
- Aircraft-specific reference fuel-burn inputs
- Aircraft range validation
- Total fuel estimation
- Total CO₂ estimation
- **CO₂ per passenger**
- Fuel mass-to-volume conversion for cost estimation
- Aircraft comparisons
- Data visualisation

The application automatically displays the number of airports, airlines and aircraft directly from the Python databases so these figures remain auditable from the source code.

---

## 🧭 How the Model Works

### 1. Great-Circle Distance

The application first calculates the geodesic distance between the selected origin and destination airports.

The published methodology then applies a global average route correction:

```text
D_corrected = 1.099 × D_great-circle
```

The correction accounts for the fact that actual flight paths are generally longer than the theoretical great-circle route.

### 2. LTO and CCD Segmentation

The model separates flight operation into:

**Landing and Take-Off (LTO)**

- Idle / taxi: 26.0 minutes
- Approach: 4.0 minutes
- Climb-out: 2.2 minutes
- Take-off: 0.7 minutes

and:

**Climb–Cruise–Descent (CCD)**

The CCD duration is estimated from corrected route distance and aircraft cruise speed.

### 3. Cruise-Time Equations

Cruise duration is calculated using the piecewise equations reported in the published methodology.

For CCD duration `t' < 60 min`:

```text
t_CR = -4.7 + 0.33t'
```

For `60 ≤ t' ≤ 120 min`:

```text
t_CR = -42 + 0.97t'
```

For `t' > 120 min`:

```text
t_CR = -48 + 0.99t'
```

The remaining non-cruise CCD duration is divided between climb and descent as a documented implementation assumption.

### 4. CCD Fuel Estimate and Correction

The current implementation uses the aircraft reference fuel-burn input as the aircraft-level slope in a transparent linear CCD model:

```text
F_CCD = a × T_CCD + b
```

where the stored aircraft reference fuel-burn value supplies `a` and the current implementation uses `b = 0`.

The calculated CCD fuel total is then distributed across climb, cruise and descent using the correction-factor structure described in the research:

```text
f_FF = F_CCD / Σ(FF0 × t)
```

followed by:

```text
FF_adjusted = f_FF × FF0
```

This ensures that the phase-level fuel totals remain consistent with the calculated total CCD fuel.

### Important Implementation Note

The published paper describes averaged normalized fuel-flow values but does not tabulate a complete numerical set of engine-specific `FF0` values or regression intercepts for all 25 aircraft currently included in the application.

The software therefore uses transparent normalized phase weights to distribute the already-calculated aircraft-level fuel total rather than presenting unverified values as engine-specific ICAO EEDB measurements.

This assumption is explicitly documented so that the model remains reproducible and its limitations are visible in the source code.

### 5. CO₂ Calculation

Fuel is retained as a **mass in kilograms** throughout the emissions calculation.

The published CO₂ emission index is:

```text
3.149 kg CO₂ / kg fuel
```

Therefore:

```text
Total CO₂ = Total fuel × 3.149
```

and:

```text
CO₂ per passenger = Total CO₂ / Number of passengers
```

CO₂ per passenger is displayed as a primary application output.

### 6. Fuel Mass and Volume

Fuel mass and volume are not treated as interchangeable.

The emissions model uses:

```text
kg of fuel
```

For the optional fuel-cost estimate only, the application converts mass to approximate volume using:

```text
Jet-fuel density assumption = 0.80 kg/L
```

Therefore:

```text
Fuel volume (L) = Fuel mass (kg) / 0.80
```

The fuel price is user-adjustable and is **not described as a live market price**.

---

## ⚠️ Input Validation

The application prevents several unrealistic inputs.

It:

- Rejects calculations where the origin and destination airport are identical.
- Checks corrected route distance against the aircraft's listed range.
- Rejects passenger counts above the aircraft's listed typical capacity.
- Keeps fuel mass in kilograms until a separate volume conversion is required.
- Allows all 25 aircraft in the database to be selected directly.

---
## 📊 Validation Against the ICAO Carbon Emissions Calculator

To evaluate the model against an independent aviation-emissions
reference, five representative routes were checked directly using the
official ICAO Carbon Emissions Calculator on **4 October 2026**.

For each ICAO calculation, the settings were:

- One Way
- Economy
- 1 passenger

The application calculations used a specifically selected aircraft and
approximately 80% of that aircraft's listed typical seating capacity.

| Route | App Aircraft | App CO₂/Pax | ICAO CO₂/Pax | Absolute % Difference |
|---|---|---:|---:|---:|
| LHE–KHI | Airbus A320 | 103.0 kg | 105 kg | 1.9% |
| LHR–CDG | Airbus A320 | 54.8 kg | 50 kg | 9.6% |
| LHE–DXB | Boeing 777-300ER | 211.8 kg | 146 kg | 45.1% |
| LHR–JFK | Boeing 787-9 Dreamliner | 525.8 kg | 303 kg | 73.5% |
| DXB–SYD | Airbus A380-800 | 1239.7 kg | 830 kg | 49.4% |

Percentage difference was calculated as:

```text
|Application − ICAO|
-------------------- × 100
        ICAO

## 🐘 A380 / Earlier Prototype Difference

The aircraft database used by the current application is different from the early prototype shown in the published paper screenshots.

The current database contains:

```text
Airbus A380-800 reference fuel burn: 11,500 kg/h
Boeing 737-800 reference fuel burn: 2,600 kg/h
```

The current A380 reference value is therefore approximately **4.42 times** the Boeing 737-800 reference value.

The near-equal A380/737 result visible in an earlier published application screenshot is not reproduced by the current aircraft database. The aircraft database was subsequently expanded and revised during development, including the modular aircraft-data update documented in July 2026.

The published paper itself has not been altered.

---

## 🧰 Technology Stack

| Area | Technology |
|---|---|
| Programming | Python |
| Web Application | Streamlit |
| Data Handling | Pandas |
| Visualisation | Altair |
| Geographic Calculations | geopy / geodesic |
| Version Control | Git & GitHub |
| Deployment | Streamlit Community Cloud |

---

## 📁 Repository Structure

```text
flight-emissions-app/
├── app.py
├── calculations.py
├── aircraft.py
├── airports.py
├── airlines.py
├── validation_helper.py
├── requirements.txt
├── runapp.sh
├── .gitignore
└── README.md
```

### Files

- `app.py` — user interface, validation and presentation
- `calculations.py` — distance, flight-phase, fuel and emissions methodology
- `aircraft.py` — 25-aircraft database
- `airports.py` — 31-airport coordinate database
- `airlines.py` — four airline fleet filters
- `validation_helper.py` — ICAO comparison helper
- `requirements.txt` — Python dependencies

---

## 🔬 Research Background

This application developed alongside my research into aviation emissions and computational modelling through the **RISE Research Scholar Programme**.

I conducted ten weeks of research under one-on-one mentorship from **Yuiko Ichikawa**, who holds a **PhD in Meteorology from the University of Hokkaido** and an **MPhil in Data Intensive Science from the University of Cambridge**.

The research examined aviation-emission estimation, ICAO emissions factors, QAR, ADS-B and simulated-flight-data methodologies, regression-based fuel-consumption approaches, and the limitations of publicly accessible aviation datasets.

The resulting research was published as:

### *Regression-Based Modeling of Flight Emissions and Per-Passenger Climate Impact*

**Muhammad Hadi — Sole Author**

International Journal for Multidisciplinary Research (IJFMR)  
Volume 8, Issue 1, January–February 2026

**[Read the Published Paper](https://www.ijfmr.com/research-paper.php?id=67871)**

---

## ⚠️ Model Limitations

This application is an educational, first-order estimation tool. It is not intended for operational flight planning, regulatory reporting, or certified aircraft-performance analysis.

Actual fuel use can vary because of:

- Payload
- Passenger load
- Cargo
- Aircraft and engine variant
- Wind
- Weather
- Altitude
- Routing
- Air traffic restrictions
- Taxi and holding time
- Airline operating procedures
- Aircraft age and configuration

The current aircraft fuel-burn values are approximate modelling inputs and should not be interpreted as flight-specific measured fuel flow.

---

## 💻 Running Locally

Clone the repository:

```bash
git clone https://github.com/muhammad7hadii/flight-emissions-app.git
cd flight-emissions-app
```

Create a virtual environment.

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

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run app.py
```

---

## 🌿 Development Workflow

The repository uses separate stable and development branches.

```text
main
└── stable / deployed application

methodology-v2
└── methodology corrections and testing
```

Changes are tested on the development branch before being merged into `main`.

---

## 📈 Changelog

### Version 2.0 — 3 October 2026

Post-publication methodology alignment and software review.

Changes:

- Applied the paper's `1.099 × great-circle distance` correction.
- Introduced explicit LTO and CCD flight-phase separation.
- Added ICAO standard LTO time-in-mode values.
- Implemented the published piecewise CCD cruise-duration equations.
- Added the fuel-flow correction-factor structure described in the paper.
- Corrected fuel-unit handling so fuel mass remains in kilograms during emissions calculations.
- Added an explicit kg-to-litre conversion only for fuel-cost estimation.
- Removed the claim that the fuel price is automatically/live adjusted.
- Made CO₂ per passenger a headline output.
- Added validation preventing identical origin and destination airports.
- Added passenger-capacity validation.
- Expanded the aircraft selector so all 25 database aircraft are accessible.
- Added visible database counts for 31 airports, 4 airlines and 25 aircraft.
- Documented the current A380/737 reference fuel-burn difference.
- Added a five-route ICAO validation framework.
- Separated development work from the stable deployed branch.

The published research paper has **not** been changed.

### Version 1.1 — July 2026

- Refactored aircraft, airport and airline data into dedicated Python modules.
- Expanded the aircraft database to 25 commercial aircraft.
- Added airline fleet filtering.
- Added aircraft-specific reference values.
- Added aircraft specifications.
- Added aircraft range checking.
- Added aircraft comparison and visualisation.
- Improved the code structure for future expansion.

---

## 👤 Author

**Muhammad Hadi**

- [Engineering Maker Portfolio](https://muhammad7hadii.github.io/hadi-maker-portfolio/)
- [LinkedIn](https://www.linkedin.com/in/muhammad-hadi-9a4661386/)
- [GitHub](https://github.com/muhammad7hadii)

---

*This project is an educational research and estimation tool and is not intended for operational flight planning or regulatory emissions reporting.*
