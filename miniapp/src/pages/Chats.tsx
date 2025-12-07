import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  MessageCircle,
  ArrowLeft,
  Clock,
  User
} from 'lucide-react';
import { Card } from '../components/common/Card';
import { useTelegram } from '../hooks/useTelegram';
import { chatsApi } from '../api/chats';

export const Chats: React.FC = () => {
  const navigate = useNavigate();
  const { hapticFeedback } = useTelegram();

  // Загружаем чаты проектов клиента
  const { data: chats, isLoading } = useQuery({
    queryKey: ['chats'],
    queryFn: () => chatsApi.getChats(),
    refetchInterval: 5000, // Обновляем каждые 5 секунд
  });

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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new':
        return 'bg-blue-500';
      case 'in_progress':
        return 'bg-yellow-500';
      case 'completed':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'только что';
    if (diffMins < 60) return `${diffMins} мин назад`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} ч назад`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} дн назад`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 pb-20">
      {/* Header */}
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-10"
      >
        <div className="px-6 py-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => {
                hapticFeedback('light');
                navigate('/');
              }}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-6 h-6 text-gray-700 dark:text-gray-300" />
            </button>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Чаты по проектам
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Общение с исполнителями
              </p>
            </div>
            <MessageCircle className="w-8 h-8 text-emerald-500" />
          </div>
        </div>
      </motion.div>

      {/* Chats List */}
      <div className="px-6 py-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
          </div>
        ) : !chats || chats.length === 0 ? (
          <Card className="text-center py-12">
            <MessageCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Нет активных чатов
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Чаты появятся когда у вас будут проекты
            </p>
          </Card>
        ) : (
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="space-y-4"
          >
            {chats.map((chat: any) => (
              <motion.div key={chat.id} variants={itemVariants}>
                <Card
                  hoverable
                  onClick={() => {
                    hapticFeedback('medium');
                    navigate(`/chats/${chat.id}`);
                  }}
                  className="relative"
                >
                  {/* Непрочитанные сообщения - бейдж */}
                  {chat.unread_by_client > 0 && (
                    <div className="absolute top-4 right-4 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
                      {chat.unread_by_client}
                    </div>
                  )}

                  <div className="flex items-start gap-4">
                    {/* Аватар проекта */}
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white font-bold text-lg flex-shrink-0">
                      {chat.project.title.substring(0, 1).toUpperCase()}
                    </div>

                    <div className="flex-1 min-w-0">
                      {/* Название проекта */}
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-1 truncate">
                        {chat.project.title}
                      </h3>

                      {/* Исполнитель */}
                      {chat.project.executor && (
                        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
                          <User className="w-4 h-4" />
                          <span>Исполнитель: {chat.project.executor.name}</span>
                        </div>
                      )}

                      {/* Последнее сообщение */}
                      {chat.last_message && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 truncate mb-1">
                          {chat.last_message.sender_type === 'client' ? 'Вы: ' : 'Исполнитель: '}
                          {chat.last_message.message_text || '📎 Вложение'}
                        </p>
                      )}

                      {/* Время последнего сообщения */}
                      {chat.last_message_at && (
                        <div className="flex items-center gap-1 text-xs text-gray-500">
                          <Clock className="w-3 h-3" />
                          <span>{formatTime(chat.last_message_at)}</span>
                        </div>
                      )}

                      {/* Статус проекта */}
                      <div className="mt-2 flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${getStatusColor(chat.project.status)}`} />
                        <span className="text-xs text-gray-600 dark:text-gray-400">
                          {chat.project.status === 'new' && 'Новый'}
                          {chat.project.status === 'in_progress' && 'В работе'}
                          {chat.project.status === 'completed' && 'Завершен'}
                        </span>
                      </div>
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
};
