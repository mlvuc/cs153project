import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'

const CHIPS = [
  {
    label: '2hr ETL by 5pm today',
    prompt: 'I need to run a 2-hour ETL pipeline that has to finish by 5pm today.',
  },
  {
    label: '6hr training by 9am tomorrow',
    prompt: 'Schedule a 6-hour model training job before 9am tomorrow.',
  },
  {
    label: 'Cheapest 1hr window tonight',
    prompt: "What's the cheapest 1-hour window to run a job tonight?",
  },
]

export default function Chat({ onJobScheduled }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function sendMessage(text) {
    if (!text.trim() || streaming) return

    setMessages(prev => [
      ...prev,
      { role: 'user', content: text },
      { role: 'assistant', content: '' },
    ])
    setInput('')
    setStreaming(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let fullContent = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop()

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          let data
          try { data = JSON.parse(line.slice(6)) } catch { continue }

          if (data.token) {
            fullContent += data.token
            setMessages(prev => [
              ...prev.slice(0, -1),
              { role: 'assistant', content: fullContent },
            ])
          }

          if (data.error) {
            setMessages(prev => [
              ...prev.slice(0, -1),
              { role: 'assistant', content: `Sorry, something went wrong: ${data.error}` },
            ])
          }

          if (data.done) {
            data.new_jobs?.forEach(job => onJobScheduled(job))
            setStreaming(false)
          }
        }
      }
    } catch (err) {
      setMessages(prev => [
        ...prev.slice(0, -1),
        { role: 'assistant', content: 'Connection error — is the backend running?' },
      ])
      setStreaming(false)
    }
  }

  return (
    <div className="chat">
      <div className="messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>
              Hi! Tell me about a job you need to run and I'll find the optimal
              energy window for it.
            </p>
            <div className="chips">
              {CHIPS.map(chip => (
                <button
                  key={chip.label}
                  className="chip"
                  onClick={() => sendMessage(chip.prompt)}
                >
                  {chip.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="bubble">
              {msg.role === 'assistant' ? (
                msg.content
                  ? <ReactMarkdown>{msg.content}</ReactMarkdown>
                  : <span className="cursor" />
              ) : (
                msg.content
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="input-area">
        <form
          className="input-row"
          onSubmit={e => { e.preventDefault(); sendMessage(input) }}
        >
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="e.g. Run a 4-hour training job before tomorrow morning…"
            disabled={streaming}
          />
          <button className="send-btn" type="submit" disabled={streaming || !input.trim()}>
            ↑
          </button>
        </form>
      </div>
    </div>
  )
}
