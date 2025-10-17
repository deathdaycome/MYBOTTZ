import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { projectsApi } from '../api/projects';
import { Button } from '../components/common/Button';
import { useTelegram } from '../hooks/useTelegram';
import { Search, FileEdit, Clock, DollarSign, ChevronRight, Plus } from 'lucide-react';

export const Projects = () => {
  const navigate = useNavigate();
  const { BackButton } = useTelegram();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // Кнопка "Назад" ведёт на Dashboard
  useEffect(() => {
    BackButton.show();
    BackButton.onClick(() => navigate('/'));

    return () => {
      BackButton.hide();
    };
  }, [BackButton, navigate]);

  // Получаем проекты
  const { data: projects = [], isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      console.log('🔄 Запрос проектов...');
      const result = await projectsApi.getMyProjects();
      console.log('✅ Получено проектов:', result?.length || 0);
      console.log('📦 Данные:', result);
      return result;
    },
  });

  console.log('🎯 Projects компонент - проекты:', projects);
  console.log('⚠️ Ошибка:', error);

  // Фильтрация проектов
  const filteredProjects = projects.filter((project) => {
    const matchesSearch = project.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || project.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusConfig = (status: string) => {
    const configs: Record<string, { label: string; color: string; emoji: string }> = {
      new: { label: 'Новый', color: 'bg-blue-100 text-blue-800', emoji: '🆕' },
      in_progress: { label: 'В работе', color: 'bg-yellow-100 text-yellow-800', emoji: '⚙️' },
      testing: { label: 'Тестирование', color: 'bg-purple-100 text-purple-800', emoji: '🧪' },
      completed: { label: 'Завершён', color: 'bg-green-100 text-green-800', emoji: '✅' },
      on_hold: { label: 'На паузе', color: 'bg-gray-100 text-gray-800', emoji: '⏸️' },
    };
    return configs[status] || configs.new;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Загрузка проектов...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-red-50 to-red-100 p-4">
        <div className="text-center bg-white p-6 rounded-xl shadow-lg max-w-md">
          <p className="text-red-600 font-bold text-xl mb-2">Ошибка загрузки</p>
          <p className="text-gray-700">{String(error)}</p>
          <pre className="mt-4 text-left text-xs bg-gray-100 p-3 rounded overflow-auto max-h-40">
            {JSON.stringify(error, null, 2)}
          </pre>
        </div>
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4">
        <div className="text-center">
          <p className="text-2xl mb-2">📭</p>
          <p className="text-gray-600 font-medium">Проектов пока нет</p>
          <p className="text-gray-400 text-sm mt-2">Создайте свой первый проект через бота</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      {/* Шапка с градиентом */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white">
        <div className="px-4 pt-6 pb-8">
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-3xl font-bold mb-2"
          >
            Мои проекты
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="text-primary-100"
          >
            Всего проектов: {projects.length}
          </motion.p>
        </div>
      </div>

      {/* Поиск и фильтры */}
      <div className="px-4 -mt-6 mb-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-lg p-4 space-y-3"
        >
          {/* Поиск */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Поиск по проектам..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            />
          </div>

          {/* Фильтры статусов */}
          <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
            {[
              { value: 'all', label: 'Все', emoji: '📋' },
              { value: 'new', label: 'Новые', emoji: '🆕' },
              { value: 'in_progress', label: 'В работе', emoji: '⚙️' },
              { value: 'testing', label: 'Тестирование', emoji: '🧪' },
              { value: 'completed', label: 'Готово', emoji: '✅' },
            ].map((filter) => (
              <button
                key={filter.value}
                onClick={() => setStatusFilter(filter.value)}
                className={'flex-shrink-0 px-4 py-2 rounded-xl font-medium transition-all ' + 
                  (statusFilter === filter.value
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  )}
              >
                <span className="mr-1">{filter.emoji}</span>
                {filter.label}
              </button>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Список проектов */}
      <div className="px-4 pb-24 space-y-4">
        <AnimatePresence mode="popLayout">
          {filteredProjects.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-white rounded-2xl shadow-sm p-12 text-center"
            >
              <div className="text-6xl mb-4">📂</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {searchTerm || statusFilter !== 'all' ? 'Проекты не найдены' : 'Нет проектов'}
              </h3>
              <p className="text-gray-600 mb-6">
                {searchTerm || statusFilter !== 'all'
                  ? 'Попробуйте изменить фильтры'
                  : 'Создайте свой первый проект'}
              </p>
              {!searchTerm && statusFilter === 'all' && (
                <Button onClick={() => navigate('/create-project')}>
                  <Plus className="w-5 h-5 mr-2" />
                  Создать проект
                </Button>
              )}
            </motion.div>
          ) : (
            filteredProjects.map((project, index) => {
              const statusConfig = getStatusConfig(project.status);
              
              return (
                <motion.div
                  key={project.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={() => navigate(`/projects/${project.id}/revisions`)}
                  className="bg-white rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden cursor-pointer group"
                >
                  {/* Цветная полоска сверху */}
                  <div className="h-1.5 bg-gradient-to-r from-primary-500 to-primary-600" />
                  
                  <div className="p-5">
                    {/* Заголовок и статус */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-bold text-gray-900 mb-1 group-hover:text-primary-600 transition-colors truncate">
                          {project.title}
                        </h3>
                        {project.description && (
                          <p className="text-sm text-gray-600 line-clamp-2">
                            {project.description}
                          </p>
                        )}
                      </div>
                      <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0 ml-2 group-hover:text-primary-600 group-hover:translate-x-1 transition-all" />
                    </div>

                    {/* Статус */}
                    <div className="flex items-center gap-2 mb-4">
                      <span className={'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ' + statusConfig.color}>
                        <span>{statusConfig.emoji}</span>
                        {statusConfig.label}
                      </span>
                      {project.project_type && (
                        <span className="text-xs px-3 py-1 bg-gray-100 text-gray-700 rounded-full font-medium">
                          {String(project.project_type).includes('bot') ? '🤖 Бот' : '🌐 Веб'}
                        </span>
                      )}
                    </div>

                    {/* Метрики */}
                    <div className="grid grid-cols-2 gap-3 mb-4">
                      {project.estimated_cost && (
                        <div className="flex items-center gap-2 text-sm">
                          <DollarSign className="w-4 h-4 text-green-600" />
                          <span className="text-gray-700 font-medium">
                            {new Intl.NumberFormat('ru-RU').format(project.estimated_cost)} ₽
                          </span>
                        </div>
                      )}
                      {project.created_at && (
                        <div className="flex items-center gap-2 text-sm">
                          <Clock className="w-4 h-4 text-blue-600" />
                          <span className="text-gray-700">
                            {new Date(project.created_at).toLocaleDateString('ru-RU', {
                              day: 'numeric',
                              month: 'short',
                            })}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Кнопка правок */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/projects/${project.id}/revisions`);
                      }}
                      className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-50 to-primary-100 text-primary-700 rounded-xl font-medium hover:from-primary-100 hover:to-primary-200 transition-all group/btn"
                    >
                      <FileEdit className="w-4 h-4" />
                      <span>Правки проекта</span>
                      <ChevronRight className="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
                    </button>
                  </div>
                </motion.div>
              );
            })
          )}
        </AnimatePresence>
      </div>

      {/* FAB кнопка создания проекта */}
      {projects.length > 0 && (
        <motion.button
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => navigate('/create-project')}
          className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-full shadow-2xl flex items-center justify-center hover:shadow-primary-500/50 transition-all z-50"
        >
          <Plus className="w-8 h-8" />
        </motion.button>
      )}
    </div>
  );
};
