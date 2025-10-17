import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { revisionsApi } from '../api/revisions';
import { RevisionCard } from '../components/revisions/RevisionCard';
import { Button } from '../components/common/Button';
import { useTelegram } from '../hooks/useTelegram';
import { Plus, ArrowLeft, AlertCircle } from 'lucide-react';

export const ProjectRevisions = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { BackButton } = useTelegram();

  // Получаем правки проекта
  const { data: revisions = [], isLoading, error } = useQuery({
    queryKey: ['revisions', projectId],
    queryFn: () => revisionsApi.getProjectRevisions(Number(projectId)),
    enabled: !!projectId,
  });

  // Получаем статистику
  const { data: stats } = useQuery({
    queryKey: ['revision-stats', projectId],
    queryFn: () => revisionsApi.getProjectRevisionStats(Number(projectId)),
    enabled: !!projectId,
  });

  useEffect(() => {
    BackButton.show();
    BackButton.onClick(() => navigate('/projects'));

    return () => {
      BackButton.hide();
    };
  }, [BackButton, navigate]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Загрузка правок...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-4 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-lg p-8 text-center max-w-md">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">Ошибка загрузки</h3>
          <p className="text-gray-600 mb-6">Не удалось загрузить правки проекта</p>
          <Button onClick={() => navigate('/projects')} fullWidth>
            <ArrowLeft className="w-4 h-4 mr-2" />
            К проектам
          </Button>
        </div>
      </div>
    );
  }

  // Название проекта (берём из первой правки если есть)
  const projectTitle = revisions[0]?.project_title || 'Проект';

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50 pb-24">
      {/* Шапка с градиентом */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 text-white">
        <div className="px-4 pt-6 pb-8">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center gap-3 mb-4"
          >
            <button
              onClick={() => navigate('/projects')}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold">Правки проекта</h1>
              <p className="text-purple-100 text-sm mt-1">{projectTitle}</p>
            </div>
          </motion.div>
          
          {/* Статистика */}
          {stats && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="grid grid-cols-4 gap-3 bg-white/10 backdrop-blur-sm rounded-2xl p-4"
            >
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.total}</div>
                <div className="text-xs text-purple-100 mt-1">Всего</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.pending}</div>
                <div className="text-xs text-purple-100 mt-1">Ожидание</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.in_progress}</div>
                <div className="text-xs text-purple-100 mt-1">В работе</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-300">{stats.completed}</div>
                <div className="text-xs text-purple-100 mt-1">Готово</div>
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Список правок */}
      <div className="px-4 mt-4 space-y-3">
        <AnimatePresence mode="popLayout">
          {revisions.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-white rounded-2xl shadow-sm p-12 text-center mt-8"
            >
              <div className="text-6xl mb-4">📝</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Правок пока нет
              </h3>
              <p className="text-gray-600 mb-6">
                Создайте первую правку для этого проекта
              </p>
              <Button onClick={() => navigate(`/projects/${projectId}/revisions/new`)}>
                <Plus className="w-5 h-5 mr-2" />
                Создать правку
              </Button>
            </motion.div>
          ) : (
            revisions.map((revision, index) => (
              <motion.div
                key={revision.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ delay: index * 0.05 }}
              >
                <RevisionCard
                  revision={revision}
                  onClick={() => navigate(`/revisions/${revision.id}`)}
                />
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      {/* FAB кнопка создания правки */}
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => navigate(`/projects/${projectId}/revisions/new`)}
        className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-full shadow-2xl flex items-center justify-center hover:shadow-purple-500/50 transition-all z-50"
      >
        <Plus className="w-8 h-8" />
      </motion.button>
    </div>
  );
};
