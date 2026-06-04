const STEPS = [
  {
    n: '01',
    title: 'Describe your job',
    body: 'Tell the copilot what you need to run in plain English — duration, deadline, and job type. No forms, no config files.',
  },
  {
    n: '02',
    title: 'Scheduler finds the window',
    body: 'The engine scans the hourly energy forecast and finds the contiguous window with the lowest average price that fits before your deadline.',
  },
  {
    n: '03',
    title: 'Claude explains the recommendation',
    body: 'The LLM takes the raw scheduling output — including the top 3 candidate windows and cost/carbon trade-offs — and explains the recommendation in plain English.',
  },
]

const STACK = [
  { layer: 'LLM', tech: 'Claude via OpenRouter', detail: 'Natural language understanding and explanation generation' },
  { layer: 'Copilot', tech: 'Python + Tool Use', detail: 'Agentic loop: parse job → call scheduler → stream explanation' },
  { layer: 'Scheduler', tech: 'Greedy sliding window', detail: 'Finds minimum average-price window of length N before deadline' },
  { layer: 'Energy data', tech: 'CSV / synthetic', detail: 'Hourly price_per_mwh and carbon_intensity; EIA/WattTime ready' },
  { layer: 'Backend', tech: 'FastAPI + SSE', detail: 'REST API with streaming chat endpoint' },
  { layer: 'Frontend', tech: 'React + Vite', detail: 'Chat UI, Recharts forecast chart, live stat cards' },
]

export default function AboutPage() {
  return (
    <div className="info-page">
      <div className="page-header">
        <h2>About Energy Copilot</h2>
        <p>An LLM-powered scheduling assistant for energy-aware data center operations</p>
      </div>

      <div className="about-intro">
        <p>
          Data center operators run hundreds of flexible compute jobs every day —
          ML training runs, ETL pipelines, batch exports — that have deadlines but
          don't need to start immediately. Energy Copilot helps ops teams schedule
          these jobs to minimize electricity cost and carbon emissions by reasoning
          over real-time energy price signals.
        </p>
      </div>

      <div className="info-section">
        <h3>How it works</h3>
        <div className="steps">
          {STEPS.map(s => (
            <div className="step" key={s.n}>
              <div className="step-number">{s.n}</div>
              <div>
                <div className="step-title">{s.title}</div>
                <p>{s.body}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="info-section">
        <h3>Tech stack</h3>
        <table className="stack-table">
          <thead>
            <tr><th>Layer</th><th>Technology</th><th>Role</th></tr>
          </thead>
          <tbody>
            {STACK.map(s => (
              <tr key={s.layer}>
                <td className="stack-layer">{s.layer}</td>
                <td className="stack-tech">{s.tech}</td>
                <td className="stack-detail">{s.detail}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="info-section">
        <h3>Limitations</h3>
        <div className="info-card">
          <ul className="limitations-list">
            <li>Energy data is currently synthetic — integration with EIA or WattTime APIs is the planned next step</li>
            <li>The scheduler uses a greedy algorithm; multi-job optimization with shared cluster constraints is not yet implemented</li>
            <li>The backend uses a single shared session — not suitable for multiple simultaneous users</li>
            <li>Deadlines must be stated explicitly; the copilot cannot yet infer urgency from context</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
