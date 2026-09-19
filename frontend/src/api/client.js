// Centralized axios instance + API calls.
// Why: every page imports functions from here instead of calling axios
// directly, so the base URL and error shape are handled in one place.
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({ baseURL: BASE_URL })

export async function fetchRoles() {
  const { data } = await client.get('/api/roles')
  return data
}

export async function createSession({ role, candidateName, resumeFile }) {
  const formData = new FormData()
  formData.append('role', role)
  if (candidateName) formData.append('candidate_name', candidateName)
  formData.append('resume_file', resumeFile)

  const { data } = await client.post('/api/sessions', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function fetchNextQuestion(sessionId) {
  const { data } = await client.get(`/api/sessions/${sessionId}/next-question`)
  return data
}

export async function submitAnswer(sessionId, { questionId, answerText }) {
  const { data } = await client.post(`/api/sessions/${sessionId}/answers`, {
    question_id: questionId,
    answer_text: answerText,
  })
  return data
}

export async function completeSession(sessionId) {
  const { data } = await client.post(`/api/sessions/${sessionId}/complete`)
  return data
}

export async function fetchSummary(sessionId) {
  const { data } = await client.get(`/api/sessions/${sessionId}/summary`)
  return data
}

export async function fetchPastSessions() {
  const { data } = await client.get('/api/sessions')
  return data
}

// Extracts a clean, human-readable message from any axios error.
export function getErrorMessage(error) {
  return error?.response?.data?.detail || error?.message || 'Something went wrong.'
}
