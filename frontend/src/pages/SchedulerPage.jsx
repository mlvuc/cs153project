import { useState, useRef, useEffect } from 'react'
import Sidebar from '../components/Sidebar'
import Chat from '../components/Chat'

const MIN_WIDTH = 180
const MAX_WIDTH = 560
const DEFAULT_WIDTH = 272

export default function SchedulerPage({ forecast, jobs, onJobScheduled }) {
  const [sidebarWidth, setSidebarWidth] = useState(DEFAULT_WIDTH)
  const isResizing = useRef(false)

  function startResize() {
    isResizing.current = true
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }

  useEffect(() => {
    function onMouseMove(e) {
      if (!isResizing.current) return
      setSidebarWidth(Math.min(Math.max(e.clientX, MIN_WIDTH), MAX_WIDTH))
    }
    function onMouseUp() {
      if (!isResizing.current) return
      isResizing.current = false
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
    document.addEventListener('mousemove', onMouseMove)
    document.addEventListener('mouseup', onMouseUp)
    return () => {
      document.removeEventListener('mousemove', onMouseMove)
      document.removeEventListener('mouseup', onMouseUp)
    }
  }, [])

  return (
    <div className="scheduler-layout">
      <Sidebar
        forecast={forecast}
        jobs={jobs}
        style={{ width: sidebarWidth, minWidth: sidebarWidth }}
      />
      <div className="resize-handle" onMouseDown={startResize} />
      <Chat onJobScheduled={onJobScheduled} />
    </div>
  )
}
