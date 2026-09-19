import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { fetchNextQuestion, submitAnswer, completeSession, getErrorMessage } from '../api/client.js'
import Banner from '../components/Banner.jsx'
import Spinner from '../components/Spinner.jsx'

export default function Interview() {
  const { sessionId } = useParams()
  const navigate = useNavigate()

  const [question, setQuestion] = useState(null)
  const [answerText, setAnswerText] = useState('')
  const [loadingQuestion, setLoadingQuestion] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  // Guards against React StrictMode's intentional double-invocation of
  // effects in development, which would otherwise fire two concurrent
  // "next question" requests on mount and silently skip the first
  // question before it could be answered.
  const hasLoadedInitialQuestion = useRef(false)

  async function loadNextQuestion() {
    setLoadingQuestion(true)
    setError('')
    try {
      const q = await fetchNextQuestion(sessionId)
      setQuestion(q)
      setAnswerText('')
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoadingQuestion(false)
    }
  }

  useEffect(() => {
    if (hasLoadedInitialQuestion.current) return
    hasLoadedInitialQuestion.current = true
    loadNextQuestion()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId])

  async function handleSubmitAnswer(e) {
    e.preventDefault()
    if (!answerText.trim()) {
      setError('Please enter an answer before continuing.')
      return
    }
    setSubmitting(true)
    setError('')
    try {
      await submitAnswer(sessionId, { questionId: question.question_id, answerText })

      if (question.is_last) {
        await completeSession(sessionId)
        navigate(`/summary/${sessionId}`)
      } else {
        await loadNextQuestion()
      }
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-2xl">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-slate-800">Interview in Progress</h2>
        {question && (
          <span className="text-sm text-slate-500 font-medium">
            Question {question.sequence_number} of {question.total_questions}
          </span>
        )}
      </div>

      {question && (
        <div className="w-full bg-slate-200 rounded-full h-1.5 mb-6">
          <div
            className="bg-brand-600 h-1.5 rounded-full transition-all"
            style={{ width: `${(question.sequence_number / question.total_questions) * 100}%` }}
          />
        </div>
      )}

      <Banner type="error">{error}</Banner>

      {loadingQuestion ? (
        <Spinner label="Generating a grounded question from the knowledge base…" />
      ) : question ? (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          {question.topic && (
            <span className="inline-block text-xs font-medium text-brand-700 bg-brand-50 px-2.5 py-1 rounded-full mb-3">
              {question.topic}
            </span>
          )}
          <p className="text-slate-800 text-base leading-relaxed mb-5">
            {question.question_text || (
              <span className="text-red-500 italic">
                No question text was returned — please refresh or contact support.
              </span>
            )}
          </p>

          <form onSubmit={handleSubmitAnswer}>
            <textarea
              value={answerText}
              onChange={(e) => setAnswerText(e.target.value)}
              rows={6}
              placeholder="Type your answer here…"
              className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none"
            />
            <button
              type="submit"
              disabled={submitting}
              className="mt-4 bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-medium py-2.5 px-6 rounded-lg text-sm transition-colors"
            >
              {submitting
                ? 'Submitting…'
                : question.is_last
                ? 'Submit & Finish Interview'
                : 'Submit & Continue'}
            </button>
          </form>
        </div>
      ) : null}
    </div>
  )
}