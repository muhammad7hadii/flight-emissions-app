"""
airports.py

Airport coordinate database.

Current coverage: 31 international airports.
Coordinates are latitude/longitude pairs used for geodesic distance
calculation.
"""

airports = {
    "LHE - Lahore": (31.5216, 74.4036),
    "KHI - Karachi": (24.9065, 67.1608),
    "ISB - Islamabad": (33.5490, 72.8257),

    "DXB - Dubai": (25.2532, 55.3657),
    "AUH - Abu Dhabi": (24.4329, 54.6511),
    "DOH - Doha": (25.2731, 51.6081),

    "LHR - London Heathrow": (51.4700, -0.4543),
    "LGW - London Gatwick": (51.1537, -0.1821),
    "MAN - Manchester": (53.3537, -2.2750),

    "CDG - Paris Charles de Gaulle": (49.0097, 2.5479),
    "FRA - Frankfurt": (50.0379, 8.5622),
    "AMS - Amsterdam": (52.3105, 4.7683),

    "JFK - New York": (40.6413, -73.7781),
    "LAX - Los Angeles": (33.9416, -118.4085),
    "ORD - Chicago O'Hare": (41.9742, -87.9073),
    "ATL - Atlanta": (33.6407, -84.4277),

    "YYZ - Toronto": (43.6777, -79.6248),

    "SIN - Singapore": (1.3644, 103.9915),
    "HKG - Hong Kong": (22.3080, 113.9185),
    "NRT - Tokyo Narita": (35.7720, 140.3929),

    "PEK - Beijing": (40.0799, 116.6031),
    "PVG - Shanghai": (31.1443, 121.8083),

    "SYD - Sydney": (-33.9399, 151.1753),
    "MEL - Melbourne": (-37.6690, 144.8410),

    "JNB - Johannesburg": (-26.1367, 28.2410),
    "CAI - Cairo": (30.1219, 31.4056),

    "IST - Istanbul": (41.2753, 28.7519),

    "DEL - Delhi": (28.5562, 77.1000),
    "BOM - Mumbai": (19.0896, 72.8656),

    "BKK - Bangkok": (13.6900, 100.7501),

    "KUL - Kuala Lumpur": (2.7456, 101.7072),
}
