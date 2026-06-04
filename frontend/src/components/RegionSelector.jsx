import { useEffect, useState } from 'react'

export default function RegionSelector({ value, onChange }) {
  const [regions, setRegions] = useState([])

  useEffect(() => {
    fetch('/api/regions')
      .then(r => r.json())
      .then(setRegions)
      .catch(console.error)
  }, [])

  return (
    <div className="region-selector">
      <div className="stat-label">Grid region</div>
      <select
        className="region-select"
        value={value || ''}
        onChange={e => onChange(e.target.value || null)}
      >
        <option value="">Default (synthetic)</option>
        {regions.map(r => (
          <option key={r.id} value={r.id}>{r.name}</option>
        ))}
      </select>
      {value && regions.find(r => r.id === value) && (
        <div className="region-description">
          {regions.find(r => r.id === value).description}
        </div>
      )}
    </div>
  )
}
