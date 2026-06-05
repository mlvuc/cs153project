import json
import os
from datetime import datetime

from openai import OpenAI
from dotenv import load_dotenv

from scheduler.energy_data import get_hourly_forecast, load_or_generate
from scheduler.engine import schedule_job

load_dotenv()

# OpenRouter model ID — verify the exact string at openrouter.ai/models
MODEL = "anthropic/claude-sonnet-4-6"

# OpenAI-format tool definition (type + function wrapper, "parameters" not "input_schema")
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "schedule_job",
            "description": (
                "Schedule a compute job to minimize energy cost and carbon emissions. "
                "Returns the optimal start window, cost/carbon savings vs running immediately, "
                "and the top 3 candidate windows."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "job_name": {
                        "type": "string",
                        "description": "Short name or description of the job",
                    },
                    "duration_hours": {
                        "type": "integer",
                        "description": "How long the job runs, in whole hours",
                    },
                    "deadline_iso": {
                        "type": "string",
                        "description": "Hard deadline as an ISO 8601 string, e.g. '2026-05-18T09:00:00'",
                    },
                },
                "required": ["job_name", "duration_hours", "deadline_iso"],
            },
        },
    }
]

def _system_prompt() -> str:
    now = datetime.now()
    return f"""You are an energy-aware workload scheduling copilot for data center operations.
Your job is to help ops teams schedule compute jobs — ML training runs, batch pipelines, data exports, etc. — \
to minimize energy cost and carbon emissions.

The current date and time is: {now.strftime("%Y-%m-%d %H:%M")} (local time).
Use this to resolve relative deadlines like "tonight", "tomorrow morning", or "in 6 hours" \
into exact ISO 8601 timestamps before calling the schedule_job tool.

When a user describes a job, use the schedule_job tool to find the optimal time window. \
After receiving the result, give a clear, concise recommendation:
- When to start and why that window is cheapest
- State cost savings as a percentage. If savings are 0% (the optimal window is right now), say so \
explicitly: "Starting now is already optimal — no benefit to waiting."
- If the price spread across all candidate windows is less than $2/MWh, tell the user that prices \
are essentially flat and timing barely matters — they can start any time before the deadline.
- Call out any trade-offs (e.g. cheapest window has higher carbon than alternatives)
- Briefly mention the next-best window if it's meaningfully different (>$2/MWh or >10g CO₂/kWh)

Be direct. Ops teams need actionable answers, not lengthy explanations."""


def _run_tool(job_name: str, duration_hours: int, deadline_iso: str) -> dict:
    """Execute the scheduler and return a JSON-serializable result dict."""
    deadline = datetime.fromisoformat(deadline_iso)
    now = datetime.now()

    if deadline <= now:
        return {"error": f"Deadline {deadline_iso} is in the past."}

    try:
        df = load_or_generate()
        forecast = get_hourly_forecast(now, deadline, df=df)
        result = schedule_job(duration_hours, deadline, forecast, now=now)
    except ValueError as e:
        return {"error": str(e)}

    def ts(t):
        return t.isoformat() if hasattr(t, "isoformat") else str(t)

    return {
        "job_name": job_name,
        "recommended_start": ts(result["recommended_start"]),
        "recommended_end": ts(result["recommended_end"]),
        "avg_price_per_mwh": result["avg_price"],
        "avg_carbon_g_co2_per_kwh": result["avg_carbon"],
        "cost_savings_vs_now_pct": result["savings_vs_naive_pct"],
        "carbon_savings_vs_now_pct": result["carbon_savings_vs_naive_pct"],
        "naive_baseline": {
            "start": ts(result["naive_baseline"]["start"]),
            "avg_price_per_mwh": result["naive_baseline"]["avg_price"],
            "avg_carbon_g_co2_per_kwh": result["naive_baseline"]["avg_carbon"],
        },
        "top_3_windows": [
            {
                "start": ts(w["start"]),
                "end": ts(w["end"]),
                "avg_price_per_mwh": w["avg_price"],
                "avg_carbon_g_co2_per_kwh": w["avg_carbon"],
            }
            for w in result["candidate_windows"]
        ],
    }


class EnergyCopilot:
    """
    Conversational copilot that schedules data center jobs via OpenRouter + tool use.

    Maintains conversation history so follow-up questions work naturally.
    Call .reset() to start a new session.
    """

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )
        self.history: list[dict] = []
        self.scheduled_jobs: list[dict] = []  # accumulates every job scheduled this session

    def _execute_tool_call(self, tc) -> dict:
        """Run one tool call, append the result to history, and track scheduled jobs."""
        args = json.loads(tc.function.arguments)
        result = _run_tool(**args)
        if "error" not in result:
            self.scheduled_jobs.append(result)
        self.history.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": json.dumps(result),
        })
        return result

    def chat(self, user_message: str) -> str:
        """Send a message, execute any tool calls, and return the final response."""
        self.history.append({"role": "user", "content": user_message})

        while True:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": _system_prompt()}] + self.history,
                tools=TOOLS,
                tool_choice="auto",
            )
            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason

            assistant_entry: dict = {"role": "assistant", "content": message.content}
            if message.tool_calls:
                assistant_entry["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in message.tool_calls
                ]
            self.history.append(assistant_entry)

            if finish_reason == "stop":
                return message.content

            for tc in message.tool_calls:
                self._execute_tool_call(tc)

    def stream_chat(self, user_message: str):
        """
        Like chat() but yields the final response token by token.

        Tool calls are handled non-streaming (they're fast and internal).
        The final explanation is streamed for a real-time feel.
        """
        self.history.append({"role": "user", "content": user_message})

        # Agentic loop: resolve all tool calls non-streaming
        tool_calls_made = False
        while True:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": _system_prompt()}] + self.history,
                tools=TOOLS,
                tool_choice="auto",
            )
            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason

            if finish_reason == "stop":
                if not tool_calls_made:
                    # Direct answer with no tool use — yield the response we have
                    self.history.append({"role": "assistant", "content": message.content})
                    yield message.content
                    return
                # Tool calls are done; break out to stream the final response
                break

            # Append assistant turn with tool_calls to history
            tool_calls_made = True
            self.history.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in message.tool_calls
                ],
            })
            for tc in message.tool_calls:
                self._execute_tool_call(tc)

        # Stream the final explanation (no tools passed — this is text-only)
        stream = self.client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": _system_prompt()}] + self.history,
            stream=True,
        )
        full_content = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_content += text
                yield text

        self.history.append({"role": "assistant", "content": full_content})

    def reset(self):
        """Clear conversation history and job queue to start a fresh session."""
        self.history = []
        self.scheduled_jobs = []
