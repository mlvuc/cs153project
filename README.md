# Energy-Aware Data Center Workload Orchestration Copilot

An LLM-powered copilot that helps data center ops teams schedule compute jobs (ML training runs, batch pipelines, etc.) to minimize energy cost and carbon emissions by reasoning over energy price signals.

## Project Structure

```
cs153project/
├── data/                   # Energy price CSVs (auto-generated if absent)
├── scheduler/
│   ├── energy_data.py      # Load/generate hourly price + carbon forecasts
│   └── engine.py           # Greedy sliding-window scheduler
├── copilot/                # Claude API integration layer (coming soon)
├── frontend/               # Chat UI (coming soon)
├── demo.ipynb              # End-to-end scheduling demo
├── requirements.txt
└── .env.example
```

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env       # add your ANTHROPIC_API_KEY when ready
jupyter notebook demo.ipynb
```

## How It Works

1. **Energy data pipeline** (`scheduler/energy_data.py`): Loads hourly `price_per_mwh` and `carbon_intensity` from a CSV. Falls back to realistic synthetic data (fixed seed, dual-peak daily curve) if no CSV is present.

2. **Scheduler** (`scheduler/engine.py`): For each job — defined by a duration and deadline — finds the contiguous window with the lowest average energy price that completes before the deadline. Returns the recommended window, a naive baseline (start immediately), and the top-3 candidates for LLM explanation.

3. **LLM copilot** (`copilot/`, coming soon): Claude API layer that accepts natural-language job descriptions, calls the scheduler, and explains the recommendation in plain English.

## Example Output

Three jobs scheduled from 8:00 AM on May 17:

| Job | Duration | Deadline | Recommended Start | Cost Savings |
|-----|----------|----------|-------------------|-------------|
| ETL pipeline | 2 hr | 2:00 PM | lowest-cost 2hr window | ~15–25% |
| Model training | 6 hr | Tomorrow 9 AM | overnight low-price window | ~20–35% |
| Data export | 1 hr | 11:00 AM | cheapest available hour | ~5–15% |
