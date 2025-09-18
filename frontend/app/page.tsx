'use client'
import { useState } from 'react'
const API = process.env.NEXT_PUBLIC_API_BASE_URL!

export default function Home() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null); setLoading(true)
    const form = new FormData(e.currentTarget)
    const payload = {
      full_name: form.get('full_name'),
      email: form.get('email'),
      phone: form.get('phone') || null,
      dob: form.get('dob'),
      zip_code: form.get('zip_code'),
      gender: form.get('gender') || null,
      address: form.get('address'),
      consent: !!form.get('consent'),
    }

    try {
      const res = await fetch(`${API}/leads/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      const token = data.session_token
      localStorage.setItem('session_token', token)
      window.location.href = `/chat?session=${token}`
    } catch (e: any) {
      setError(e.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold">Find Your Retirement & Insurance Plan</h1>
        <p className="text-sm text-gray-600">Fill the form to start a quick personalized chat.</p>
      </header>

      <form onSubmit={onSubmit} className="grid grid-cols-1 gap-4 bg-white p-6 rounded-2xl shadow">
        <input name="full_name" placeholder="Full Name" className="border p-2 rounded" required />
        <input type="email" name="email" placeholder="Email" className="border p-2 rounded" required />
        <input name="phone" placeholder="Phone (optional)" className="border p-2 rounded" />
        <input type="date" name="dob" placeholder="Date of Birth" className="border p-2 rounded" required />
        <input name="zip_code" placeholder="Zip Code" className="border p-2 rounded" required />
        <select name="gender" className="border p-2 rounded">
          <option value="">Gender (optional)</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
        </select>
        <textarea name="address" placeholder="Full Address" className="border p-2 rounded" required />
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" name="consent" defaultChecked required />
          I agree to be contacted and accept the privacy policy.
        </label>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button disabled={loading} className="bg-black text-white rounded-xl py-2">
          {loading ? 'Submitting…' : 'Start Chat'}
        </button>
      </form>
    </div>
  )
}
