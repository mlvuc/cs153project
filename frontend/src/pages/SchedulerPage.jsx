import Sidebar from '../components/Sidebar'
import Chat from '../components/Chat'

export default function SchedulerPage({ forecast, jobs, onJobScheduled }) {
  return (
    <div className="scheduler-layout">
      <Sidebar forecast={forecast} jobs={jobs} />
      <Chat onJobScheduled={onJobScheduled} />
    </div>
  )
}
