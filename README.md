# Energy Copilot — Energy-Aware Data Center Workload Scheduler

An LLM-powered copilot that helps data center ops teams schedule compute jobs — ML training runs, batch ETL pipelines, data exports — to minimize electricity cost and carbon emissions by reasoning over hourly energy price signals.

---

## Overview

Data centers spend 30–50% of their operating budget on energy, and electricity prices can swing 4x across a single day. Most compute workloads are deadline-tolerant (they need to finish by a certain time, but don't need to start immediately), yet ops teams almost always run them immediately. Energy Copilot closes that gap.

You describe a job in plain English. The copilot identifies the duration and deadline, runs a scheduling algorithm over the energy forecast for your grid region, and streams back a plain-English recommendation explaining the optimal start window, cost and carbon savings, and the top alternative windows.

---

## Project Structure

```
cs153project/
├── backend/
│   └── main.py              # FastAPI server — /forecast, /chat (SSE), /regions, /reset
├── scheduler/
│   ├── energy_data.py       # Load/generate hourly price + carbon data
│   ├── engine.py            # Greedy sliding-window scheduling algorithm
│   └── regions.py           # 7 real-world grid region profiles
├── copilot/
│   └── planner.py           # Claude copilot layer with tool use + streaming
├── frontend/
│   ├── src/
│   │   ├── components/      # Sidebar, Chat, ForecastChart, RegionSelector
│   │   └── pages/           # Scheduler, Forecast, DataCenters, About
│   └── package.json
├── demo.ipynb                # Standalone scheduling demo (no API key needed)
├── requirements.txt
└── .env.example
```

---

## Setup

**Requirements:** Python 3.11+, Node.js 18+

```bash
# 1. Clone and install Python dependencies
git clone https://github.com/mlvuc/cs153project.git
cd cs153project
pip install -r requirements.txt

# 2. Add your API key
cp .env.example .env
# Open .env and set: OPENROUTER_API_KEY=your_key_here

# 3. Install frontend dependencies
cd frontend
npm install
cd ..
```

Get a free OpenRouter API key at [openrouter.ai](https://openrouter.ai). The scheduler and demo notebook work without any API key.

---

## Running the App

Open two terminal windows:

**Terminal 1 — backend:**

```bash
cd cs153project
uvicorn backend.main:app --reload
```

**Terminal 2 — frontend:**

```bash
cd cs153project/frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## Usage

**Scheduler page:** Describe a compute job in plain English. Include the job type, estimated duration, and deadline. Examples:

- _"We need to fine-tune a 7B parameter language model on 50GB of text. Estimated 6 hours on 8x H100s. Must complete before our 9am deployment window tomorrow."_
- _"Run our nightly ETL pipeline — about 3 hours. Data science team needs fresh data before 7am standups."_
- _"Batch inference job across 80 million user sessions, roughly 2 hours. Product team needs results by 2pm today."_

**Grid region selector:** Switch between CAISO (California), ERCOT (Texas), PJM (Mid-Atlantic), MISO (Midwest), ISONE (New England), NYISO (New York), and NORDPOOL (Nordics) to see how recommendations change across grids with different price patterns and carbon intensity.

**Forecast page:** View the full 24-hour price and carbon intensity forecast with an hourly breakdown table.

**Demo notebook:** Run `jupyter notebook demo.ipynb` for a standalone demo that schedules three example jobs and produces a chart — no API key required.

---

## How It Works

1. **Energy data pipeline** (`scheduler/energy_data.py`): Loads hourly `price_per_mwh` and `carbon_intensity` from CSV. Falls back to synthetic data if no CSV is present. Seven regional profiles (`scheduler/regions.py`) model real grid characteristics — price levels, daily curve shapes, and carbon intensity by fuel mix.

2. **Scheduling engine** (`scheduler/engine.py`): Greedy sliding-window algorithm — scans all contiguous windows of `duration_hours` that complete before the deadline, picks the one with the lowest average price. Returns the recommended window, naive baseline (start now), cost/carbon savings, and top-3 candidates.

3. **LLM copilot** (`copilot/planner.py`): Claude (via OpenRouter) receives the natural-language job description and calls the scheduler as a tool. The current date/time is injected into the system prompt so relative deadlines ("tomorrow morning", "in 6 hours") resolve correctly. After the tool call, Claude streams a plain-English explanation back to the user.

4. **Backend** (`backend/main.py`): FastAPI with endpoints — `GET /forecast?region=X` returns the energy forecast, `POST /chat` streams the copilot response via Server-Sent Events, `GET /regions` returns available grid profiles.

5. **Frontend** (`frontend/`): React + Vite with a resizable sidebar showing live stat cards and a Recharts dual-axis forecast chart. Responses render with full markdown support including tables.

---

## Known Limitations

- Energy data is synthetic and based on regional averages — not live market prices. Integration with EIA or WattTime APIs is the planned next step.
- The scheduler optimizes one job at a time. Multi-job queue optimization with shared cluster constraints is not yet implemented.
- The backend uses a single shared session — not suitable for multiple simultaneous users in production.

---

## AI Usage Disclosure

This project was built with assistance from **Claude Code** (Anthropic's AI coding assistant) and the **Claude API** (accessed via OpenRouter).

Claude Code was used as a development tool throughout this project, primarily for code generation, debugging, and iterating on the UI. The problem framing and product concept was entirely built by me. Then, I used Claude as a brainstorming source to come up with ideas. However, the final architectural decisions and direction of what to build were driven by me. I designed the overall system: the idea of combining a domain-specific scheduling algorithm with an LLM explanation layer, the choice to use tool use rather than asking the LLM to do the optimization directly, the grid region profiles, the multi-page React layout, and the demo scenarios. I reviewed and tested the outputs and directed changes.

The Claude API powers the copilot layer itself — Claude receives job descriptions, calls the scheduler tool, and generates recommendations.

---

## Acknowledgements & Citations

- **OpenRouter** — API gateway used to access Claude: [openrouter.ai](https://openrouter.ai)
- **Anthropic / Claude** — LLM powering the copilot layer: [anthropic.com](https://www.anthropic.com)
- **FastAPI** — Python backend framework: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **React + Vite** — Frontend framework: [react.dev](https://react.dev), [vitejs.dev](https://vitejs.dev)
- **Recharts** — React charting library: [recharts.org](https://recharts.org)
- **EIA (U.S. Energy Information Administration)** — Regional grid price and carbon intensity data used to calibrate synthetic profiles: [eia.gov](https://www.eia.gov)
- **Electricity Maps** — Carbon intensity data referenced for regional profiles: [electricitymaps.com](https://www.electricitymaps.com)
- Grid price pattern research: _U.S. Electric System Operating Data_, EIA-930
