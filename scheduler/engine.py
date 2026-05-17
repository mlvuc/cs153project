from datetime import datetime, timedelta
from typing import Any


def schedule_job(
    duration_hours: int,
    deadline: datetime,
    energy_forecast: list[dict],
    now: datetime = None,
) -> dict[str, Any]:
    """
    Greedy sliding-window scheduler: find the cheapest contiguous window
    of `duration_hours` that completes before `deadline`.

    Returns the recommended schedule, naive baseline (start now), and the
    top-3 candidate windows so the LLM layer can explain trade-offs.
    """
    if now is None:
        now = datetime.now()

    available = sorted(
        [
            h for h in energy_forecast
            if h["timestamp"] >= now
            and h["timestamp"] + timedelta(hours=1) <= deadline
        ],
        key=lambda x: x["timestamp"],
    )

    if len(available) < duration_hours:
        raise ValueError(
            f"Only {len(available)} hours before deadline; need {duration_hours}"
        )

    # Naive baseline: start at the first available hour
    naive_window = available[:duration_hours]
    naive_avg_price = _avg(naive_window, "price")
    naive_avg_carbon = _avg(naive_window, "carbon")

    # Greedy: scan all windows, pick the one with minimum average price
    best_idx, best_avg_price = 0, float("inf")
    for i in range(len(available) - duration_hours + 1):
        avg = _avg(available[i: i + duration_hours], "price")
        if avg < best_avg_price:
            best_avg_price = avg
            best_idx = i

    best_window = available[best_idx: best_idx + duration_hours]
    best_avg_carbon = _avg(best_window, "carbon")

    return {
        "recommended_start": best_window[0]["timestamp"],
        "recommended_end": best_window[-1]["timestamp"] + timedelta(hours=1),
        "window": best_window,
        "avg_price": round(best_avg_price, 2),
        "avg_carbon": round(best_avg_carbon, 1),
        "savings_vs_naive_pct": round(
            (naive_avg_price - best_avg_price) / naive_avg_price * 100, 1
        ),
        "carbon_savings_vs_naive_pct": round(
            (naive_avg_carbon - best_avg_carbon) / naive_avg_carbon * 100, 1
        ),
        "naive_baseline": {
            "start": naive_window[0]["timestamp"],
            "avg_price": round(naive_avg_price, 2),
            "avg_carbon": round(naive_avg_carbon, 1),
        },
        "candidate_windows": _top_windows(available, duration_hours),
    }


def _avg(window: list[dict], key: str) -> float:
    return sum(h[key] for h in window) / len(window)


def _top_windows(available: list[dict], duration_hours: int, n: int = 3) -> list[dict]:
    """Top n lowest-cost windows — passed to the LLM layer for explanation."""
    candidates = []
    for i in range(len(available) - duration_hours + 1):
        w = available[i: i + duration_hours]
        candidates.append({
            "start": w[0]["timestamp"],
            "end": w[-1]["timestamp"] + timedelta(hours=1),
            "avg_price": round(_avg(w, "price"), 2),
            "avg_carbon": round(_avg(w, "carbon"), 1),
        })
    return sorted(candidates, key=lambda x: x["avg_price"])[:n]
