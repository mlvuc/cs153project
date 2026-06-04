import { useState, useEffect } from 'react'
import SchedulerPage from './pages/SchedulerPage'
import ForecastPage from './pages/ForecastPage'
import DataCentersPage from './pages/DataCentersPage'
import AboutPage from './pages/AboutPage'
import './App.css'

const NAV = [
  { id: 'scheduler',    label: 'Scheduler' },
  { id: 'forecast',     label: 'Forecast' },
  { id: 'datacenters',  label: 'Data Centers' },
  { id: 'about',        label: 'About' },
]

export default function App() {
  const [page, setPage] = useState('scheduler')
  const [jobs, setJobs] = useState([])
  const [forecast, setForecast] = useState(null)

  useEffect(() => {
    fetch('/api/forecast')
      .then(r => r.json())
      .then(setForecast)
      .catch(console.error)
  }, [])

  function addJob(job) {
    setJobs(prev => [...prev, job])
  }

  return (
    <div className="app">

      {/* ── Top navbar ── */}
      <nav className="navbar">
        <div className="navbar-brand">
          <span className="navbar-icon">⚡</span>
          Energy Copilot
        </div>
        <div className="navbar-nav">
          {NAV.map(item => (
            <button
              key={item.id}
              className={`nav-item ${page === item.id ? 'active' : ''}`}
              onClick={() => setPage(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>
        <div className="navbar-right">
          <span className="live-dot">●</span>
          <span className="live-label">Live</span>
          {forecast && <span className="live-price">${forecast.current_price}/MWh</span>}
        </div>
      </nav>

      {/* ── Page content ── */}
      <div className="page-content">
        {page === 'scheduler' && (
          <SchedulerPage
            forecast={forecast}
            jobs={jobs}
            onJobScheduled={addJob}
          />
        )}
        {page === 'forecast'    && <ForecastPage forecast={forecast} />}
        {page === 'datacenters' && <DataCentersPage />}
        {page === 'about'       && <AboutPage />}
      </div>

    </div>
  )
}
