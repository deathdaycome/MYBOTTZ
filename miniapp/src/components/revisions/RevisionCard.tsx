import { motion } from 'framer-motion';
import { RevisionBadge } from './RevisionBadge';
import { ProgressBar } from './ProgressBar';
import type { Revision } from '../../types/revision';

interface RevisionCardProps {
  revision: Revision;
  onClick: () => void;
}

export const RevisionCard = ({ revision, onClick }: RevisionCardProps) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Сегодня';
    if (diffDays === 1) return 'Вчера';
    if (diffDays < 7) return `${diffDays} дн. назад`;
    
    return date.toLocaleDateString('ru-RU');
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 cursor-pointer hover:shadow-md transition-shadow"
    >
      {/* Заголовок */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 mb-1">
            #{revision.revision_number} - {revision.title}
          </h3>
          <p className="text-sm text-gray-600 line-clamp-2">
            {revision.description}
          </p>
        </div>
      </div>

      {/* Прогресс-бар */}
      {revision.status === 'in_progress' && (
        <div className="mb-3">
          <ProgressBar 
            progress={revision.progress} 
            timeSpentSeconds={revision.time_spent_seconds}
          />
        </div>
      )}

      {/* Статус и приоритет */}
      <div className="flex items-center gap-2 mb-3">
        <RevisionBadge type="status" value={revision.status} />
        <RevisionBadge type="priority" value={revision.priority} />
      </div>

      {/* Дата */}
      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>📅 {formatDate(revision.created_at)}</span>
        {revision.assigned_to_username && (
          <span>👤 {revision.assigned_to_username}</span>
        )}
      </div>
    </motion.div>
  );
};
