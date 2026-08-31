import { Navigate, Route, Routes } from 'react-router-dom'

import { AppShell } from './components/layout/AppShell'
import { useLearnerSession } from './context/LearnerSessionContext'
import { CoursesPage } from './pages/CoursesPage'
import { DashboardPage } from './pages/DashboardPage'
import { OnboardingChatPage } from './pages/OnboardingChatPage'
import { ProfilePage } from './pages/ProfilePage'
import { RoadmapPage } from './pages/RoadmapPage'

function HomeRedirect() {
  const { learnerId } = useLearnerSession()
  return <Navigate to={learnerId ? '/dashboard' : '/onboarding'} replace />
}

function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<HomeRedirect />} />
        <Route path="/onboarding" element={<OnboardingChatPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/roadmap" element={<RoadmapPage />} />
        <Route path="/courses" element={<CoursesPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="*" element={<HomeRedirect />} />
      </Routes>
    </AppShell>
  )
}

export default App
