const FACTS = [
  {
    stat: '~1–2%',
    label: 'of global electricity',
    detail: 'Data centers currently consume between 200–250 TWh per year worldwide — comparable to the entire country of Argentina.',
  },
  {
    stat: '30–50%',
    label: 'of OpEx is energy',
    detail: 'For large hyperscale operators, energy is the single largest operating expense, often exceeding hardware and staffing costs.',
  },
  {
    stat: '4×',
    label: 'price swing per day',
    detail: 'Electricity prices can vary by 4x or more across a 24-hour period due to demand cycles, renewable generation, and grid conditions.',
  },
  {
    stat: '~200g',
    label: 'CO₂ per kWh (avg)',
    detail: 'The average grid carbon intensity in the US. Running jobs at off-peak hours — when more renewables are online — can cut this by 30–50%.',
  },
]

const HOW = [
  {
    title: 'Peak pricing',
    body: 'Electricity grids price power dynamically. Morning and evening peaks (when demand surges) are 2–4× more expensive than overnight hours. Batch workloads that can tolerate a few hours of delay can save significantly.',
  },
  {
    title: 'Carbon follows renewables',
    body: 'Solar and wind generation push carbon intensity down mid-day and overnight. Running compute during these windows shrinks the carbon footprint of the same workload.',
  },
  {
    title: 'Flexible workloads are common',
    body: "ML training runs, ETL pipelines, batch exports, and model evaluation jobs are all deadline-tolerant — they need to finish by some point, but don't need to start immediately. This makes them ideal for price-aware scheduling.",
  },
]

export default function DataCentersPage() {
  return (
    <div className="info-page">
      <div className="page-header">
        <h2>Data Centers & Energy</h2>
        <p>Why energy-aware scheduling matters at scale</p>
      </div>

      <div className="info-stats-grid">
        {FACTS.map(f => (
          <div className="info-stat-card" key={f.stat}>
            <div className="info-stat-number">{f.stat}</div>
            <div className="info-stat-label">{f.label}</div>
            <div className="info-stat-detail">{f.detail}</div>
          </div>
        ))}
      </div>

      <div className="info-section">
        <h3>Why prices change</h3>
        <div className="info-cards">
          {HOW.map(h => (
            <div className="info-card" key={h.title}>
              <div className="info-card-title">{h.title}</div>
              <p>{h.body}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="info-section">
        <h3>The opportunity</h3>
        <div className="info-opportunity">
          <p>
            A large ML training cluster running 24/7 at $70/MWh average cost
            could save <strong>$2–4M per year</strong> by shifting flexible workloads
            to off-peak windows — with no change to hardware or software, just smarter scheduling.
          </p>
          <p>
            The same shift can reduce the cluster's carbon footprint by
            <strong> 20–40%</strong>, supporting sustainability commitments without
            buying offsets.
          </p>
          <p>
            This is the problem Energy Copilot is designed to solve — starting with
            a conversational interface that makes optimal scheduling accessible to
            any ops team, not just those with dedicated energy analysts.
          </p>
        </div>
      </div>
    </div>
  )
}
