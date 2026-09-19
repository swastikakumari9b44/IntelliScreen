import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchSummary, getErrorMessage } from '../api/client.js'
import Banner from '../components/Banner.jsx'
import Spinner from '../components/Spinner.jsx'

export default function Summary() {
  const { sessionId } = useParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchSummary(sessionId)
      .then(setData)
      .catch((e) => setError(getErrorMessage(e)))
      .finally(() => setLoading(false))
  }, [sessionId])

  if (loading) return <Spinner label="Loading summary…" />
  if (error) return <Banner type="error">{error}</Banner>
  if (!data) return null

  const { session, qa_pairs, insights } = data

  return (
    <div className="max-w-3xl">
      <div className="flex items-center justify-between mb-1">
        <h2 className="text-2xl font-bold text-slate-800">Interview Summary</h2>
        <Link to="/new" className="text-sm text-brand-600 hover:underline">
          Start another interview
        </Link>
      </div>
      <p className="text-slate-500 text-sm mb-6">
        {session.candidate_name || 'Candidate'} · {session.role} · {session.status}
      </p>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <StatCard label="Questions" value={insights.total_questions} />
        <StatCard label="Answered" value={insights.total_answered} />
        <StatCard label="Topics Covered" value={insights.topics_covered.length} />
      </div>

      {insights.skills_touched.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6">
          <h3 className="text-sm font-semibold text-slate-700 mb-2">Skills from Resume</h3>
          <div className="flex flex-wrap gap-2">
            {insights.skills_touched.map((s) => (
              <span key={s} className="text-xs bg-slate-100 text-slate-600 px-2.5 py-1 rounded-full">
                {s}
              </span>
            ))}
          </div>
        </div>
      )}

      <h3 className="text-sm font-semibold text-slate-700 mb-3">Full Transcript</h3>
      <div className="space-y-4">
        {qa_pairs.map((qa) => (
          <div key={qa.sequence_number} className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-medium text-slate-400">Q{qa.sequence_number}</span>
              {qa.topic && (
                <span className="text-xs font-medium text-brand-700 bg-brand-50 px-2 py-0.5 rounded-full">
                  {qa.topic}
                </span>
              )}
            </div>
            <p className="text-slate-800 font-medium mb-3">{qa.question_text}</p>
            <p className="text-slate-600 text-sm bg-slate-50 rounded-lg p-3">
              {qa.answer_text || <span className="text-slate-400 italic">Not answered</span>}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

function StatCard({ label, value }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 text-center">
      <div className="text-2xl font-bold text-brand-600">{value}</div>
      <div className="text-xs text-slate-500 mt-1">{label}</div>
    </div>
  )
}
