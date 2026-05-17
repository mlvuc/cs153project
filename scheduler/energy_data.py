import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_CSV = DATA_DIR / "energy_prices.csv"


def generate_synthetic_data(days: int = 7, start_date: datetime = None) -> pd.DataFrame:
    """7 days of synthetic hourly prices with realistic dual-peak daily patterns."""
    rng = np.random.default_rng(42)
    if start_date is None:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    records = []
    for day in range(days):
        for hour in range(24):
            ts = start_date + timedelta(days=day, hours=hour)

            # Morning peak ~8am, evening peak ~7pm
            base = 45.0
            morning = 30 * np.exp(-0.5 * ((hour - 8) / 2) ** 2)
            evening = 25 * np.exp(-0.5 * ((hour - 19) / 2) ** 2)
            price = max(base + morning + evening + rng.normal(0, 3), 15.0)

            # Carbon intensity peaks midday (more fossil backup under high grid load)
            carbon = max(
                250.0 + 80 * np.exp(-0.5 * ((hour - 14) / 4) ** 2) + rng.normal(0, 10),
                150.0,
            )

            records.append({
                "timestamp": ts,
                "price_per_mwh": round(price, 2),
                "carbon_intensity": round(carbon, 1),
            })

    return pd.DataFrame(records)


def load_or_generate(csv_path: str = None) -> pd.DataFrame:
    """Load CSV if it exists, otherwise generate and cache synthetic data."""
    path = Path(csv_path) if csv_path else DEFAULT_CSV
    if path.exists():
        df = pd.read_csv(path, parse_dates=["timestamp"])
    else:
        df = generate_synthetic_data()
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(DEFAULT_CSV, index=False)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def get_price_forecast(date, csv_path: str = None) -> list[dict]:
    """Return [{hour, price, carbon, timestamp}, ...] for a single calendar day."""
    df = load_or_generate(csv_path)
    target = pd.Timestamp(date).normalize()
    day_df = df[df["timestamp"].dt.normalize() == target]
    if day_df.empty:
        raise ValueError(f"No energy data for {date}")
    return _df_to_records(day_df)


def get_hourly_forecast(
    start_dt: datetime,
    end_dt: datetime,
    df: pd.DataFrame = None,
    csv_path: str = None,
) -> list[dict]:
    """Return hourly forecast entries in [start_dt, end_dt)."""
    if df is None:
        df = load_or_generate(csv_path)
    mask = (df["timestamp"] >= pd.Timestamp(start_dt)) & (
        df["timestamp"] < pd.Timestamp(end_dt)
    )
    return _df_to_records(df[mask])


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    return [
        {
            "hour": row.timestamp.hour,
            "price": row.price_per_mwh,
            "carbon": row.carbon_intensity,
            "timestamp": row.timestamp,
        }
        for row in df.itertuples()
    ]
