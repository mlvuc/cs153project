import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from 'recharts'

export default function ForecastChart({ data }) {
  if (!data || !data.length) {
    return <div className="chart-placeholder">Loading…</div>
  }

  return (
    <ResponsiveContainer width="100%" height={160}>
      <LineChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
        <XAxis
          dataKey="time"
          tick={{ fill: '#4b5563', fontSize: 9 }}
          interval={5}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          yAxisId="price"
          tick={{ fill: '#00d4aa', fontSize: 9 }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          yAxisId="carbon"
          orientation="right"
          tick={{ fill: '#ff6b6b', fontSize: 9 }}
          tickLine={false}
          axisLine={false}
          width={28}
        />
        <Tooltip
          contentStyle={{
            background: '#1a1d2e',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: '8px',
            fontSize: '0.75rem',
          }}
          labelStyle={{ color: '#9ca3af', marginBottom: '4px' }}
          itemStyle={{ color: '#e8eaf0' }}
        />
        <Line
          yAxisId="price"
          type="monotone"
          dataKey="price"
          stroke="#00d4aa"
          strokeWidth={2}
          dot={false}
          name="Price ($/MWh)"
        />
        <Line
          yAxisId="carbon"
          type="monotone"
          dataKey="carbon"
          stroke="#ff6b6b"
          strokeWidth={1.5}
          strokeDasharray="4 2"
          dot={false}
          name="Carbon (g CO₂/kWh)"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
