import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  FolderKanban,
  MessageCircle,
  TrendingUp,
  Clock
} from 'lucide-react';
import { Card } from '../components/common/Card';
import { useTelegram } from '../hooks/useTelegram';
import { projectsApi } from '../api/projects';
import { revisionsApi } from '../api/revisions';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user, hapticFeedback } = useTelegram();

  // Загружаем реальную статистику из API
  const { data: projectsStats } = useQuery({
    queryKey: ['projects-stats'],
    queryFn: () => projectsApi.getProjectsStats(),
    staleTime: 0, // Данные всегда считаются устаревшими
    refetchOnMount: true, // Перезагружать при монтировании
    refetchOnWindowFocus: true, // Перезагружать при фокусе окна
  });

  const { data: revisionsStats } = useQuery({
    queryKey: ['revisions-stats'],
    queryFn: () => revisionsApi.getAllRevisionsStats(),
    staleTime: 0,
    refetchOnMount: true,
    refetchOnWindowFocus: true,
  });

  const stats = {
    totalProjects: projectsStats?.total || 0,
    inProgress: projectsStats?.in_progress || 0,
    completed: projectsStats?.completed || 0,
    totalRevisions: revisionsStats?.open || 0,
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
    },
  };

  const quickActions = [
    {
      title: 'Мои проекты',
      description: stats.totalProjects === 1 ? '1 проект' : `${stats.totalProjects} проектов`,
      icon: <FolderKanban className="w-6 h-6" />,
      gradient: 'from-blue-500 to-cyan-500',
      action: () => {
        hapticFeedback('medium');
        navigate('/projects');
      },
    },
    {
      title: 'Чаты',
      description: 'Общение с исполнителем',
      icon: <MessageCircle className="w-6 h-6" />,
      gradient: 'from-emerald-500 to-teal-500',
      action: () => {
        hapticFeedback('medium');
        navigate('/chats');
      },
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 pb-20">
      {/* Header */}
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-10"
      >
        <div className="px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Привет, {user?.first_name || 'Пользователь'}! 👋
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Добро пожаловать в ИИ логист
              </p>
            </div>
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white font-bold text-xl">
              {user?.first_name?.[0] || 'U'}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Stats Cards */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="px-6 py-6 grid grid-cols-2 gap-4"
      >
        <motion.div variants={itemVariants}>
          <Card className="relative overflow-hidden">
            <div className="absolute top-0 right-0 w-20 h-20 bg-blue-100 dark:bg-blue-900/20 rounded-full -mr-10 -mt-10" />
            <div className="relative">
              <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 mb-2">
                <TrendingUp className="w-5 h-5" />
                <span className="text-sm font-medium">Всего</span>
              </div>
              <div className="text-3xl font-bold text-gray-900 dark:text-white">
                {stats.totalProjects}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                проектов
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="relative overflow-hidden">
            <div className="absolute top-0 right-0 w-20 h-20 bg-yellow-100 dark:bg-yellow-900/20 rounded-full -mr-10 -mt-10" />
            <div className="relative">
              <div className="flex items-center gap-2 text-yellow-600 dark:text-yellow-400 mb-2">
                <Clock className="w-5 h-5" />
                <span className="text-sm font-medium">В работе</span>
              </div>
              <div className="text-3xl font-bold text-gray-900 dark:text-white">
                {stats.inProgress}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                проекта
              </div>
            </div>
          </Card>
        </motion.div>
      </motion.div>

      {/* Main Sections */}
      <div className="px-6 py-2">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Разделы
        </h2>
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-2 gap-4"
        >
          {quickActions.map((action, index) => (
            <motion.div key={index} variants={itemVariants}>
              <Card
                hoverable
                onClick={action.action}
                className="relative overflow-hidden h-full"
              >
                <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${action.gradient} opacity-10 rounded-full -mr-16 -mt-16`} />
                <div className="relative">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${action.gradient} flex items-center justify-center text-white mb-3`}>
                    {action.icon}
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                    {action.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {action.description}
                  </p>
                </div>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  );
};
