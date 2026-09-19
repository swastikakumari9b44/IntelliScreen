import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchRoles, createSession, getErrorMessage } from '../api/client.js'
import Banner from '../components/Banner.jsx'
import Spinner from '../components/Spinner.jsx'

export default function NewInterview() {
  const navigate = useNavigate()
  const [roles, setRoles] = useState([])
  const [rolesLoading, setRolesLoading] = useState(true)
  const [selectedRole, setSelectedRole] = useState('')
  const [candidateName, setCandidateName] = useState('')
  const [resumeFile, setResumeFile] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchRoles()
      .then((data) => {
        setRoles(data)
        if (data.length > 0) setSelectedRole(data[0].id)
      })
      .catch((e) => setError(getErrorMessage(e)))
      .finally(() => setRolesLoading(false))
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (!resumeFile) {
      setError('Please upload your resume (PDF) before continuing.')
      return
    }
    if (!selectedRole) {
      setError('Please select a role.')
      return
    }

    setSubmitting(true)
    try {
      const result = await createSession({
        role: selectedRole,
        candidateName: candidateName || undefined,
        resumeFile,
      })
      navigate(`/interview/${result.session_id}`)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-2xl">
      <h2 className="text-2xl font-bold text-slate-800 mb-1">Start a New Interview</h2>
      <p className="text-slate-500 mb-6 text-sm">
        Upload a resume and select a role. Questions will be generated from a
        role-specific knowledge base, grounded in the candidate's background.
      </p>

      <Banner type="error">{error}</Banner>

      {rolesLoading ? (
        <Spinner label="Loading roles…" />
      ) : (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-slate-200 p-6 space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              Candidate Name <span className="text-slate-400">(optional)</span>
            </label>
            <input
              type="text"
              value={candidateName}
              onChange={(e) => setCandidateName(e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              placeholder="e.g. Jane Doe"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              Target Role
            </label>
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              {roles.map((r) => (
                <option key={r.id} value={r.id}>{r.label}</option>
              ))}
            </select>
            {roles.find((r) => r.id === selectedRole) && (
              <p className="text-xs text-slate-400 mt-1">
                {roles.find((r) => r.id === selectedRole).description}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              Resume (PDF)
            </label>
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
              className="w-full text-sm text-slate-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-brand-50 file:text-brand-700 file:text-sm file:font-medium hover:file:bg-brand-100"
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-medium py-2.5 rounded-lg text-sm transition-colors"
          >
            {submitting ? 'Setting up interview…' : 'Start Interview'}
          </button>
        </form>
      )}
    </div>
  )
}
