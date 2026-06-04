import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid,
  ResponsiveContainer, ReferenceLine,
} from 'recharts'

export default function ForecastPage({ forecast }) {
  if (!forecast) {
    return <div className="page-loading">Loading forecast…</div>
  }

  const { data, current_price, cheapest_hour, avg_carbon } = forecast

  return (
    <div className="forecast-page">
      <div className="page-header">
        <h2>Energy Forecast</h2>
        <p>Live energy price and carbon intensity for the next 24 hours</p>
      </div>

      <div className="forecast-stats">
        <div className="fstat-card">
          <div className="fstat-label">Current Price</div>
          <div className="fstat-value">${current_price}<span>/MWh</span></div>
        </div>
        <div className="fstat-card highlight">
          <div className="fstat-label">Cheapest Hour</div>
          <div className="fstat-value">${cheapest_hour.price}<span>/MWh</span></div>
          <div className="fstat-sub">at {cheapest_hour.time}</div>
        </div>
        <div className="fstat-card">
          <div className="fstat-label">Avg Carbon Intensity</div>
          <div className="fstat-value">{avg_carbon}<span> g CO₂/kWh</span></div>
        </div>
        <div className="fstat-card">
          <div className="fstat-label">Potential Savings</div>
          <div className="fstat-value">
            {Math.round((current_price - cheapest_hour.price) / current_price * 100)}
            <span>%</span>
          </div>
          <div className="fstat-sub">vs running now</div>
        </div>
      </div>

      <div className="forecast-chart-card">
        <div className="chart-title">Price & Carbon — Next 24 Hours</div>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={data} margin={{ top: 8, right: 40, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis
              dataKey="time"
              tick={{ fill: '#6b7280', fontSize: 11 }}
              interval={2}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              yAxisId="price"
              tick={{ fill: '#00d4aa', fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              label={{ value: '$/MWh', angle: -90, position: 'insideLeft', fill: '#00d4aa', fontSize: 11, dx: -4 }}
            />
            <YAxis
              yAxisId="carbon"
              orientation="right"
              tick={{ fill: '#ff6b6b', fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              label={{ value: 'g CO₂/kWh', angle: 90, position: 'insideRight', fill: '#ff6b6b', fontSize: 11, dx: 8 }}
            />
            <Tooltip
              contentStyle={{
                background: '#1a1d2e',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '10px',
                fontSize: '0.8rem',
              }}
              labelStyle={{ color: '#9ca3af', marginBottom: 4 }}
            />
            <ReferenceLine
              yAxisId="price"
              y={cheapest_hour.price}
              stroke="rgba(0,212,170,0.25)"
              strokeDasharray="4 3"
              label={{ value: 'cheapest', fill: 'rgba(0,212,170,0.5)', fontSize: 10, position: 'right' }}
            />
            <Line
              yAxisId="price" type="monotone" dataKey="price"
              stroke="#00d4aa" strokeWidth={2.5} dot={false} name="Price ($/MWh)"
            />
            <Line
              yAxisId="carbon" type="monotone" dataKey="carbon"
              stroke="#ff6b6b" strokeWidth={2} strokeDasharray="5 3"
              dot={false} name="Carbon (g CO₂/kWh)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="forecast-table-card">
        <div className="chart-title">Hourly Breakdown</div>
        <div className="forecast-table-wrap">
          <table className="forecast-table">
            <thead>
              <tr>
                <th>Hour</th>
                <th>Price ($/MWh)</th>
                <th>Carbon (g CO₂/kWh)</th>
                <th>vs Average</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row, i) => {
                const avgPrice = data.reduce((s, r) => s + r.price, 0) / data.length
                const diff = row.price - avgPrice
                return (
                  <tr key={i} className={row.price === cheapest_hour.price ? 'cheapest-row' : ''}>
                    <td>{row.time}</td>
                    <td>${row.price.toFixed(1)}</td>
                    <td>{row.carbon}</td>
                    <td className={diff < 0 ? 'below-avg' : 'above-avg'}>
                      {diff < 0 ? '▼' : '▲'} ${Math.abs(diff).toFixed(1)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
