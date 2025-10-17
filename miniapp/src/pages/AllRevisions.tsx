import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { FileEdit, ArrowLeft, Clock, CheckCircle2, AlertCircle, XCircle } from 'lucide-react';
import { useTelegram } from '../hooks/useTelegram';
import { projectsApi } from '../api/projects';
import { revisionsApi } from '../api/revisions';
import { RevisionCard } from '../components/revisions/RevisionCard';
import type { Revision } from '../types/revision';

export const AllRevisions = () => {
  const navigate = useNavigate();
  const { BackButton } = useTelegram();

  // Настраиваем кнопку "Назад"
  BackButton.onClick(() => navigate('/'));
  BackButton.show();

  // Загружаем все правки пользователя
  const { data: allRevisionsData, isLoading, error } = useQuery({
    queryKey: ['all-revisions'],
    queryFn: async () => {
      console.log('🔄 Загрузка всех правок...');

      // Получаем список всех проектов
      const projects = await projectsApi.getMyProjects();
      console.log('📦 Получено проектов:', projects.length);

      // Для каждого проекта получаем правки
      const allRevisions: Revision[] = [];

      for (const project of projects) {
        try {
          console.log(`  📂 Проект ${project.id} (${project.title})`);
          const revData = await revisionsApi.getProjectRevisions(project.id);
          console.log(`    Ответ API:`, revData);
          console.log(`    Тип revData:`, Array.isArray(revData) ? 'массив' : 'объект');

          // revData уже может быть массивом благодаря обработке в revisionsApi
          const revisions = Array.isArray(revData) ? revData : ((revData as any)?.revisions || []);
          console.log(`    Правок найдено:`, revisions.length);

          if (revisions.length > 0) {
            allRevisions.push(...revisions);
          }
        } catch (err) {
          console.error(`❌ Ошибка получения правок для проекта ${project.id}:`, err);
        }
      }

      console.log('✅ Всего правок загружено:', allRevisions.length);
      return allRevisions;
    },
  });

  const revisions = allRevisionsData || [];

  // Статистика
  const stats = {
    total: revisions.length,
    pending: revisions.filter(r => r.status === 'pending').length,
    in_progress: revisions.filter(r => r.status === 'in_progress').length,
    completed: revisions.filter(r => r.status === 'completed').length,
    rejected: revisions.filter(r => r.status === 'rejected').length,
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Загрузка правок...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <p className="text-red-800 font-medium">Ошибка загрузки</p>
          <p className="text-red-600 text-sm mt-1">{(error as Error).message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-6">
      {/* Gradient Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 text-white">
        <div className="px-4 pt-6 pb-8">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center gap-3 mb-4"
          >
            <button
              onClick={() => navigate('/')}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-6 h-6" />
            </button>
            <div>
              <h1 className="text-3xl font-bold">Все правки</h1>
              <p className="text-purple-100 mt-1">Список всех ваших правок</p>
            </div>
          </motion.div>

          {/* Statistics */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-5 gap-2 bg-white/10 backdrop-blur-sm rounded-2xl p-4"
          >
            <div className="text-center">
              <div className="text-2xl font-bold">{stats.total}</div>
              <div className="text-xs text-purple-100 mt-1">Всего</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{stats.pending}</div>
              <div className="text-xs text-purple-100 mt-1 flex items-center justify-center gap-1">
                <Clock className="w-3 h-3" />
                Ожидание
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{stats.in_progress}</div>
              <div className="text-xs text-purple-100 mt-1 flex items-center justify-center gap-1">
                <AlertCircle className="w-3 h-3" />
                В работе
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{stats.completed}</div>
              <div className="text-xs text-purple-100 mt-1 flex items-center justify-center gap-1">
                <CheckCircle2 className="w-3 h-3" />
                Готово
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{stats.rejected}</div>
              <div className="text-xs text-purple-100 mt-1 flex items-center justify-center gap-1">
                <XCircle className="w-3 h-3" />
                Отклонено
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Revisions List */}
      <div className="px-4 mt-6">
        {revisions.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 text-center"
          >
            <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileEdit className="w-10 h-10 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Правок пока нет
            </h3>
            <p className="text-gray-600 mb-6">
              Создайте первую правку в любом из ваших проектов
            </p>
            <button
              onClick={() => navigate('/projects')}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-xl font-medium hover:shadow-lg transition-shadow"
            >
              Перейти к проектам
            </button>
          </motion.div>
        ) : (
          <div className="space-y-3">
            {revisions.map((revision, index) => (
              <motion.div
                key={revision.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <RevisionCard
                  revision={revision}
                  onClick={() => navigate(`/revisions/${revision.id}`)}
                />
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
