import type { RevisionStatus, RevisionPriority } from '../../types/revision';

interface RevisionBadgeProps {
  type: 'status' | 'priority';
  value: RevisionStatus | RevisionPriority;
}

export const RevisionBadge = ({ type, value }: RevisionBadgeProps) => {
  if (type === 'status') {
    const statusConfig = {
      pending: { emoji: '⏳', label: 'В ожидании', color: 'bg-yellow-100 text-yellow-800' },
      in_progress: { emoji: '🔄', label: 'В работе', color: 'bg-blue-100 text-blue-800' },
      completed: { emoji: '✅', label: 'Выполнено', color: 'bg-green-100 text-green-800' },
      rejected: { emoji: '❌', label: 'Отклонено', color: 'bg-red-100 text-red-800' },
      needs_rework: { emoji: '🔧', label: 'Требует доработки', color: 'bg-orange-100 text-orange-800' },
      approved: { emoji: '✔️', label: 'Одобрено', color: 'bg-emerald-100 text-emerald-800' },
    };
    
    const config = statusConfig[value as RevisionStatus];
    
    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
        <span>{config.emoji}</span>
        <span>{config.label}</span>
      </span>
    );
  }
  
  // Priority
  const priorityConfig = {
    low: { emoji: '🟢', label: 'Низкий', color: 'bg-gray-100 text-gray-800' },
    normal: { emoji: '🔵', label: 'Обычный', color: 'bg-blue-100 text-blue-800' },
    high: { emoji: '🟡', label: 'Высокий', color: 'bg-orange-100 text-orange-800' },
    urgent: { emoji: '🔴', label: 'Срочный', color: 'bg-red-100 text-red-800' },
  };
  
  const config = priorityConfig[value as RevisionPriority];
  
  return (
    <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
      <span>{config.emoji}</span>
      <span>{config.label}</span>
    </span>
  );
};
