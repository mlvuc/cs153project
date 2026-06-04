import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import Chat from './components/Chat'
import './App.css'

export default function App() {
  const [jobs, setJobs] = useState([])
  const [forecast, setForecast] = useState(null)
  const [region, setRegion] = useState(null)

  useEffect(() => {
    const url = region ? `/api/forecast?region=${region}` : '/api/forecast'
    fetch(url)
      .then(r => r.json())
      .then(setForecast)
      .catch(console.error)
  }, [region])

  function addJob(job) {
    setJobs(prev => [...prev, job])
  }

  return (
    <div className="app">
      <Sidebar
        forecast={forecast}
        jobs={jobs}
        region={region}
        onRegionChange={setRegion}
      />
      <div className="main">
        <header className="header">
          <div className="header-left">
            <span className="header-icon">⚡</span>
            <div>
              <h1>Energy-Aware Workload Scheduler</h1>
              <p>
                {forecast?.region_name
                  ? `${forecast.region_name} · ${forecast.region_description}`
                  : 'Describe a job — get the cheapest, cleanest window to run it'}
              </p>
            </div>
          </div>
          <div className="header-right">
            <span className="live-dot">●</span>
            <span className="live-label">Live</span>
            {forecast && (
              <span className="live-price">${forecast.current_price}/MWh</span>
            )}
          </div>
        </header>
        <Chat onJobScheduled={addJob} />
      </div>
    </div>
  )
}
