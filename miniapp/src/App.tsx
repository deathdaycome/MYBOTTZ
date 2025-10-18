import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Dashboard } from './pages/Dashboard';
import { Projects } from './pages/Projects';
import { ProjectRevisions } from './pages/ProjectRevisions';
import { AllRevisions } from './pages/AllRevisions';
import { RevisionChat } from './pages/RevisionChat';
import { CreateRevision } from './pages/CreateRevision';
import { TestRevisions } from './pages/TestRevisions';
import { QuickProjectCreate } from './pages/QuickProjectCreate';
import Documents from './pages/Documents';
import Finance from './pages/Finance';
import Notifications from './pages/Notifications';
import { useTelegram } from './hooks/useTelegram';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  const { isReady } = useTelegram();

  if (!isReady) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Загрузка...</p>
        </div>
      </div>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/projects/quick-create" element={<QuickProjectCreate />} />
          <Route path="/projects/:projectId/revisions" element={<ProjectRevisions />} />
          <Route path="/projects/:projectId/revisions/new" element={<CreateRevision />} />
          <Route path="/revisions" element={<AllRevisions />} />
          <Route path="/revisions/:revisionId" element={<RevisionChat />} />
          <Route path="/test-revisions" element={<TestRevisions />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/finance" element={<Finance />} />
          <Route path="/notifications" element={<Notifications />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
