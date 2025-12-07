import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import { FontProvider } from './contexts/FontContext'
import { AuthProvider } from './contexts/AuthContext'
import { Layout } from './components/layout/Layout'
import { PrivateRoute } from './components/PrivateRoute'
import { Login } from './pages/Login'
import { Dashboard } from './pages/Dashboard'
import { Projects } from './pages/Projects'
import { ProjectView } from './pages/ProjectView'
import { ProjectOverview } from './pages/project/ProjectOverview'
import { ProjectTasks } from './pages/project/ProjectTasks'
import { ProjectRevisions } from './pages/project/ProjectRevisions'
import { ProjectChat } from './pages/project/ProjectChat'
import { ProjectDocuments } from './pages/project/ProjectDocuments'
import { ProjectFinance } from './pages/project/ProjectFinance'
import { ProjectHosting } from './pages/project/ProjectHosting'
import { Tasks } from './pages/Tasks'
import { Revisions } from './pages/Revisions'
import { Clients } from './pages/Clients'
import { Leads } from './pages/Leads'
import { Deals } from './pages/Deals'
import { Contractors } from './pages/Contractors'
import { ProjectFiles } from './pages/ProjectFiles'
import { TasksArchive } from './pages/TasksArchive'
import { MyTasks } from './pages/MyTasks'
import { Chats } from './pages/Chats'
import { ChatDetail } from './pages/ChatDetail'
import { Avito } from './pages/Avito'
import { Documents } from './pages/Documents'
import { Portfolio } from './pages/Portfolio'
import { Finance } from './pages/Finance'
import { Services } from './pages/Services'
import { Analytics } from './pages/Analytics'
import { Reports } from './pages/Reports'
import { Notifications } from './pages/Notifications'
import { Automation } from './pages/Automation'
import { Hosting } from './pages/Hosting'
import { Permissions } from './pages/Permissions'
import { Users } from './pages/Users'
import { Settings } from './pages/Settings'
import { Transcription } from './pages/Transcription'
import { AICalls } from './pages/AICalls'
import { AICallsV2 } from './pages/AICallsV2'
import { TimleadRegulations } from './pages/TimleadRegulations'

function App() {
  // В разработке используем "/", в продакшене "/admin" (соответствует vite.config.ts)
  const basename = import.meta.env.MODE === 'production' ? '/admin' : '/'

  return (
    <FontProvider>
      <ThemeProvider>
        <AuthProvider>
          <BrowserRouter basename={basename}>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route element={<PrivateRoute />}>
                <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="projects" element={<Projects />} />

            {/* Карточка проекта с вкладками */}
            <Route path="projects/:projectId" element={<ProjectView />}>
              <Route index element={<Navigate to="overview" replace />} />
              <Route path="overview" element={<ProjectOverview />} />
              <Route path="tasks" element={<ProjectTasks />} />
              <Route path="revisions" element={<ProjectRevisions />} />
              <Route path="chat" element={<ProjectChat />} />
              <Route path="documents" element={<ProjectDocuments />} />
              <Route path="finance" element={<ProjectFinance />} />
              <Route path="hosting" element={<ProjectHosting />} />
            </Route>

            <Route path="project-files" element={<ProjectFiles />} />
            <Route path="tasks" element={<Tasks />} />
            <Route path="tasks-archive" element={<TasksArchive />} />
            <Route path="my-tasks" element={<MyTasks />} />
            <Route path="revisions" element={<Revisions />} />
            <Route path="clients" element={<Clients />} />
            <Route path="leads" element={<Leads />} />
            <Route path="deals" element={<Deals />} />
            <Route path="contractors" element={<Contractors />} />
            <Route path="chats" element={<Chats />} />
            <Route path="chats/:chatId" element={<ChatDetail />} />
            <Route path="avito" element={<Avito />} />
            <Route path="documents" element={<Documents />} />
            <Route path="portfolio" element={<Portfolio />} />
            <Route path="finance" element={<Finance />} />
            <Route path="services" element={<Services />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="reports" element={<Reports />} />
            <Route path="notifications" element={<Notifications />} />
            <Route path="automation" element={<Automation />} />
            <Route path="hosting" element={<Hosting />} />
            <Route path="permissions" element={<Permissions />} />
            <Route path="users" element={<Users />} />
            <Route path="settings" element={<Settings />} />
            <Route path="transcription" element={<Transcription />} />
            <Route path="ai-calls" element={<AICalls />} />
            <Route path="ai-calls-v2" element={<AICallsV2 />} />
            <Route path="timlead-regulations" element={<TimleadRegulations />} />
              </Route>
            </Route>
          </Routes>
          </BrowserRouter>
        </AuthProvider>
      </ThemeProvider>
    </FontProvider>
  )
}

export default App
