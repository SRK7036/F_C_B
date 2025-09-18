'use client'
import { useEffect, useRef, useState } from 'react'
const API = process.env.NEXT_PUBLIC_API_BASE_URL!

type Msg = { role: 'user' | 'assistant'; content: string }

export default function ChatPage() {
  const [session, setSession] = useState('')
  const [messages, setMessages] = useState<Msg[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const url = new URL(window.location.href)
    const token = url.searchParams.get('session') || localStorage.getItem('session_token') || ''
    setSession(token)
  }, [])

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = async (text: string) => {
    if (!session || !text.trim()) return
    setLoading(true)
    setMessages(m => [...m, { role: 'user', content: text }])
    setInput('')
    const res = await fetch(`${API}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_token: session, message: text })
    })
    const data = await res.json()
    setMessages(m => [...m, { role: 'assistant', content: data.response }])
    setLoading(false)
  }

  const agree = async () => {
    if (!session) return
    await fetch(`${API}/actions/agree`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_token: session })
    })
    setMessages(m => [...m, { role: 'assistant', content: '✅ Saved your details and sent confirmation email.' }])
  }

  const explore = async () => {
    if (!session) return
    const pref = prompt('What would you like to change or explore more about? (e.g., lower premium, more tax benefits)') || 'Show an alternative plan'
    const res = await fetch(`${API}/actions/explore`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_token: session, preferences: pref })
    })
    const data = await res.json()
    setMessages(m => [...m, { role: 'assistant', content: data.response }])
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Personalized Plan Chat</h1>
      <div className="bg-white rounded-2xl shadow p-4 h-[60vh] overflow-y-auto">
        {messages.length === 0 && (
          <p className="text-sm text-gray-500">Say hi and share your goals (retirement, savings, tax planning, budget)…</p>
        )}
        <div className="space-y-3">
          {messages.map((m, i) => (
            <div key={i} className={m.role === 'user' ? 'text-right' : 'text-left'}>
              <span className={`inline-block px-3 py-2 rounded-2xl ${m.role === 'user' ? 'bg-black text-white' : 'bg-gray-100'}`}>{m.content}</span>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') send(input) }}
          placeholder="Type your message…"
          className="flex-1 border rounded-xl px-3 py-2"
        />
        <button onClick={() => send(input)} disabled={loading} className="px-4 py-2 rounded-xl bg-black text-white">Send</button>
      </div>
      <div className="flex gap-2">
        <button onClick={agree} className="px-4 py-2 rounded-xl bg-green-600 text-white">✅ Agree</button>
        <button onClick={explore} className="px-4 py-2 rounded-xl bg-blue-600 text-white">🔍 Explore More</button>
      </div>
    </div>
  )
}
