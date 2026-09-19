import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchPastSessions, getErrorMessage } from '../api/client.js'
import Banner from '../components/Banner.jsx'
import Spinner from '../components/Spinner.jsx'

export default function PastSessions() {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchPastSessions()
      .then(setSessions)
      .catch((e) => setError(getErrorMessage(e)))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-3xl">
      <h2 className="text-2xl font-bold text-slate-800 mb-1">Past Sessions</h2>
      <p className="text-slate-500 text-sm mb-6">All interview sessions recorded so far.</p>

      <Banner type="error">{error}</Banner>

      {loading ? (
        <Spinner label="Loading sessions…" />
      ) : sessions.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-400 text-sm">
          No sessions yet. Start a new interview to see it appear here.
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100">
          {sessions.map((s) => (
            <Link
              key={s.id}
              to={`/summary/${s.id}`}
              className="flex items-center justify-between px-5 py-4 hover:bg-slate-50 transition-colors"
            >
              <div>
                <p className="text-sm font-medium text-slate-800">
                  {s.candidate_name || 'Unnamed Candidate'}
                </p>
                <p className="text-xs text-slate-400 mt-0.5">
                  {s.role} · {new Date(s.created_at).toLocaleString()}
                </p>
              </div>
              <span
                className={`text-xs font-medium px-2.5 py-1 rounded-full ${
                  s.status === 'completed'
                    ? 'bg-green-50 text-green-700'
                    : 'bg-amber-50 text-amber-700'
                }`}
              >
                {s.status}
              </span>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
