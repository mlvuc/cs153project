"""
Region-specific energy data generator.

Each region is tuned to real grid characteristics:
  - Base price reflects actual average wholesale rates
  - Price peaks model the daily demand curve shape (duck curve for CAISO, etc.)
  - Carbon baseline and peaks reflect the fuel mix of that grid
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# (hour, magnitude, width_sigma)
# Negative magnitude = a dip (e.g. solar pushing carbon DOWN at midday)
REGIONS: dict = {
    "CAISO": {
        "name": "California (CAISO)",
        "description": "Solar-heavy grid with an evening 'duck curve' price spike",
        "base_price": 52.0,
        "price_noise": 4.0,
        "price_peaks": [(9, 12, 2.5), (19, 38, 1.5)],
        "carbon_base": 220.0,
        "carbon_peaks": [(7, 40, 2), (13, -80, 3), (20, 55, 2)],
    },
    "ERCOT": {
        "name": "Texas (ERCOT)",
        "description": "Wind-heavy, volatile grid with hot summer afternoon demand",
        "base_price": 42.0,
        "price_noise": 7.0,
        "price_peaks": [(8, 18, 2.5), (14, 22, 3.0), (18, 20, 2.0)],
        "carbon_base": 275.0,
        "carbon_peaks": [(14, 65, 4), (3, -30, 3)],
    },
    "PJM": {
        "name": "Mid-Atlantic (PJM)",
        "description": "Large mixed grid with traditional morning and evening peaks",
        "base_price": 38.0,
        "price_noise": 3.5,
        "price_peaks": [(8, 20, 2.5), (18, 22, 2.0)],
        "carbon_base": 310.0,
        "carbon_peaks": [(14, 70, 4)],
    },
    "MISO": {
        "name": "Midwest (MISO)",
        "description": "Coal and wind mix — cheap prices, higher carbon",
        "base_price": 31.0,
        "price_noise": 3.0,
        "price_peaks": [(8, 14, 3.0), (17, 16, 2.5)],
        "carbon_base": 345.0,
        "carbon_peaks": [(14, 60, 4), (3, -20, 3)],
    },
    "ISONE": {
        "name": "New England (ISO-NE)",
        "description": "High-priced grid with sharp winter morning peaks",
        "base_price": 58.0,
        "price_noise": 5.0,
        "price_peaks": [(8, 26, 2.0), (18, 22, 2.0)],
        "carbon_base": 255.0,
        "carbon_peaks": [(14, 50, 4)],
    },
    "NYISO": {
        "name": "New York (NYISO)",
        "description": "Dense urban grid with midday commercial demand peaks",
        "base_price": 48.0,
        "price_noise": 4.5,
        "price_peaks": [(9, 18, 2.5), (12, 14, 2.0), (18, 20, 2.0)],
        "carbon_base": 250.0,
        "carbon_peaks": [(13, 55, 4)],
    },
    "NORDPOOL": {
        "name": "Nordic Countries (NORDPOOL)",
        "description": "Hydro-dominant grid — very low carbon, flat prices",
        "base_price": 22.0,
        "price_noise": 2.5,
        "price_peaks": [(8, 8, 3.0), (17, 7, 3.0)],
        "carbon_base": 45.0,
        "carbon_peaks": [(14, 12, 5)],
    },
}


def generate_regional_data(
    region_id: str,
    days: int = 2,
    start_date: datetime = None,
) -> pd.DataFrame:
    """
    Generate synthetic hourly energy data tuned to a specific grid region.
    Uses fixed seed so results are reproducible for the same region.
    """
    if region_id not in REGIONS:
        raise ValueError(f"Unknown region '{region_id}'. Valid: {list(REGIONS)}")

    cfg = REGIONS[region_id]
    seed = sum(ord(c) for c in region_id)  # deterministic per region
    rng = np.random.default_rng(seed)

    if start_date is None:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    records = []
    for day in range(days):
        for hour in range(24):
            ts = start_date + timedelta(days=day, hours=hour)

            price = cfg["base_price"]
            for peak_h, mag, width in cfg["price_peaks"]:
                price += mag * np.exp(-0.5 * ((hour - peak_h) / width) ** 2)
            price += rng.normal(0, cfg["price_noise"])
            price = max(price, cfg["base_price"] * 0.25)

            carbon = cfg["carbon_base"]
            for peak_h, mag, width in cfg["carbon_peaks"]:
                carbon += mag * np.exp(-0.5 * ((hour - peak_h) / width) ** 2)
            carbon += rng.normal(0, 10)
            carbon = max(carbon, 20.0)

            records.append({
                "timestamp": ts,
                "price_per_mwh": round(float(price), 2),
                "carbon_intensity": round(float(carbon), 1),
            })

    return pd.DataFrame(records)
