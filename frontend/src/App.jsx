import { Routes, Route, Navigate } from 'react-router-dom'
import DashboardLayout from './layouts/DashboardLayout.jsx'
import NewInterview from './pages/NewInterview.jsx'
import Interview from './pages/Interview.jsx'
import Summary from './pages/Summary.jsx'
import PastSessions from './pages/PastSessions.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<DashboardLayout />}>
        <Route path="/" element={<Navigate to="/new" replace />} />
        <Route path="/new" element={<NewInterview />} />
        <Route path="/interview/:sessionId" element={<Interview />} />
        <Route path="/summary/:sessionId" element={<Summary />} />
        <Route path="/sessions" element={<PastSessions />} />
      </Route>
    </Routes>
  )
}
