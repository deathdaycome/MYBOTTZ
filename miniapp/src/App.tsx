import { useState, useEffect } from 'react';
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
import { Chats } from './pages/Chats';
import { ChatDetail } from './pages/ChatDetail';
import Documents from './pages/Documents';
import Finance from './pages/Finance';
import Notifications from './pages/Notifications';
import { Onboarding } from './components/Onboarding';
import { useTelegram } from './hooks/useTelegram';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 0, // Всегда перезагружать данные
      gcTime: 0, // Не кэшировать (gcTime заменил cacheTime в React Query v5)
    },
  },
});

const ONBOARDING_KEY = 'onboarding_completed';
const APP_VERSION = 'v2.2.6'; // Детальное логирование для отладки
const VERSION_KEY = 'app_version';

function App() {
  const { isReady } = useTelegram();
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [checkingOnboarding, setCheckingOnboarding] = useState(true);

  useEffect(() => {
    // Проверяем версию приложения и перезагружаем при обновлении
    const savedVersion = localStorage.getItem(VERSION_KEY);
    if (savedVersion !== APP_VERSION) {
      console.log('🔄 Обновление приложения: перезагрузка страницы');
      // Сохраняем новую версию
      localStorage.setItem(VERSION_KEY, APP_VERSION);
      // Принудительно перезагружаем страницу для загрузки нового кода
      window.location.reload();
      return; // Прерываем выполнение, так как страница будет перезагружена
    }

    // Проверяем, был ли показан онбординг
    const onboardingCompleted = localStorage.getItem(ONBOARDING_KEY);
    setShowOnboarding(!onboardingCompleted);
    setCheckingOnboarding(false);
  }, []);

  const handleOnboardingComplete = () => {
    localStorage.setItem(ONBOARDING_KEY, 'true');
    setShowOnboarding(false);
  };

  if (!isReady || checkingOnboarding) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Загрузка...</p>
        </div>
      </div>
    );
  }

  if (showOnboarding) {
    return <Onboarding onComplete={handleOnboardingComplete} />;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/chats" element={<Chats />} />
          <Route path="/chats/:chatId" element={<ChatDetail />} />
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
