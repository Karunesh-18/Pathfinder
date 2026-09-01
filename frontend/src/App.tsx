import { Route, Routes } from 'react-router-dom'

import { AppShell } from './components/layout/AppShell'
import { ProtectedRoute } from './components/routing/ProtectedRoute'
import { ChatbotPage } from './pages/ChatbotPage'
import { CourseDetailPage } from './pages/CourseDetailPage'
import { CoursesPage } from './pages/CoursesPage'
import { CourseTreePage } from './pages/CourseTreePage'
import { DashboardPage } from './pages/DashboardPage'
import { LandingPage } from './pages/LandingPage'
import { LoginPage } from './pages/LoginPage'
import { OnboardingChatPage } from './pages/OnboardingChatPage'
import { RoadmapPage } from './pages/RoadmapPage'
import { RolesPage } from './pages/RolesPage'
import { SettingsPage } from './pages/SettingsPage'
import { SignupPage } from './pages/SignupPage'

function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/onboarding" element={<OnboardingChatPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/roles" element={<RolesPage />} />
          <Route path="/courses" element={<CoursesPage />} />
          <Route path="/courses/tree" element={<CourseTreePage />} />
          <Route path="/courses/:courseId" element={<CourseDetailPage />} />
          <Route path="/roadmap" element={<RoadmapPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/chat" element={<ChatbotPage />} />
        </Route>

        <Route path="*" element={<LandingPage />} />
      </Routes>
    </AppShell>
  )
}

export default App
