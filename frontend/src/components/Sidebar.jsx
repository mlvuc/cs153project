import ForecastChart from './ForecastChart'

export default function Sidebar({ forecast, jobs, style }) {
  return (
    <aside className="sidebar" style={style}>
      <div className="sidebar-logo">Energy Forecast</div>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Current price</div>
          <div className="stat-value">
            {forecast ? `$${forecast.current_price}/MWh` : '—'}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Cheapest hour</div>
          <div className="stat-value">
            {forecast ? `$${forecast.cheapest_hour.price}/MWh` : '—'}
          </div>
          {forecast && <div className="stat-sub">{forecast.cheapest_hour.time}</div>}
        </div>
        <div className="stat-card wide">
          <div className="stat-label">Avg carbon (24 hr)</div>
          <div className="stat-value">
            {forecast ? `${forecast.avg_carbon} g CO₂/kWh` : '—'}
          </div>
        </div>
      </div>

      <div className="chart-section">
        <div className="section-title">Next 24 hours</div>
        <ForecastChart data={forecast?.data} />
        <div className="chart-legend">
          <span style={{ color: '#00d4aa' }}>— price</span>
          <span style={{ color: '#ff6b6b' }}>- - carbon</span>
        </div>
      </div>

      {jobs.length > 0 && (
        <div className="jobs-section">
          <div className="section-title">
            Scheduled this session ({jobs.length})
          </div>
          <table className="jobs-table">
            <thead>
              <tr>
                <th>Job</th>
                <th>Start</th>
                <th>Savings</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job, i) => (
                <tr key={i}>
                  <td title={job.job_name}>{job.job_name}</td>
                  <td>{job.recommended_start.slice(11, 16)}</td>
                  <td className="savings">
                    {job.cost_savings_vs_now_pct.toFixed(0)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </aside>
  )
}
