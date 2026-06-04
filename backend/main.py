import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from copilot.planner import EnergyCopilot
from scheduler.energy_data import load_or_generate

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

copilot = EnergyCopilot()


class ChatRequest(BaseModel):
    message: str


@app.get("/forecast")
def get_forecast():
    df = load_or_generate()
    now = pd.Timestamp(datetime.now())

    window = df[df["timestamp"] >= now].head(24)
    if window.empty:
        window = df.head(24)

    current_price = float(window["price_per_mwh"].iloc[0])
    cheapest = window.loc[window["price_per_mwh"].idxmin()]

    return {
        "current_price": round(current_price, 0),
        "cheapest_hour": {
            "price": round(float(cheapest["price_per_mwh"]), 0),
            "time": pd.Timestamp(cheapest["timestamp"]).strftime("%H:%M"),
        },
        "avg_carbon": round(float(window["carbon_intensity"].mean()), 0),
        "data": [
            {
                "time": pd.Timestamp(row.timestamp).strftime("%H:%M"),
                "price": round(float(row.price_per_mwh), 1),
                "carbon": round(float(row.carbon_intensity), 0),
            }
            for row in window.itertuples()
        ],
    }


@app.post("/chat")
def chat(request: ChatRequest):
    jobs_before = len(copilot.scheduled_jobs)

    def generate():
        try:
            for token in copilot.stream_chat(request.message):
                yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        new_jobs = copilot.scheduled_jobs[jobs_before:]
        yield f"data: {json.dumps({'done': True, 'new_jobs': new_jobs})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/reset")
def reset():
    copilot.reset()
    return {"status": "ok"}
