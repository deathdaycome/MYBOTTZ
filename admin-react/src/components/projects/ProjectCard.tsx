import {
  Eye,
  Edit,
  Trash2,
  Archive,
  CheckCircle,
  MessageCircle,
  DollarSign,
  FileText,
  UserPlus,
  File,
  Banknote,
} from 'lucide-react'
import PixelCard from '../common/PixelCard'

interface Project {
  id: number
  title: string
  description: string
  project_type: string
  status: string
  complexity: string
  priority: string
  estimated_cost: number
  executor_cost: number
  client_paid_total: number
  executor_paid_total: number
  deadline: string | null
  is_archived: boolean
  created_at: string
  user: {
    id: number
    first_name: string
    username: string
    telegram_id: number
  } | null
  assigned_to: {
    id: number
    username: string
  } | null
  chat: {
    id: number
  } | null
  payments: any[]
}

interface ProjectCardProps {
  project: Project
  onView: (id: number) => void
  onEdit: (id: number) => void
  onDelete: (id: number) => void
  onArchive: (id: number) => void
  onContact: (telegramId: number) => void
  onAddPayment: (id: number) => void
  onComplete?: (id: number) => void
  onViewFiles?: (id: number) => void
  onAssignExecutor?: (id: number) => void
  onExecutorPayment?: (id: number) => void
}

// Helper functions
const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    new: 'from-blue-400 to-blue-600',
    review: 'from-orange-400 to-orange-600',
    accepted: 'from-purple-400 to-purple-600',
    in_progress: 'from-yellow-400 to-yellow-600',
    testing: 'from-green-400 to-green-600',
    completed: 'from-green-500 to-green-700',
    cancelled: 'from-red-400 to-red-600',
    on_hold: 'from-gray-400 to-gray-600',
  }
  return colors[status] || 'from-gray-400 to-gray-600'
}

const getStatusName = (status: string) => {
  const names: Record<string, string> = {
    new: '🆕 Новый',
    review: '👀 Рассмотрение',
    accepted: '✅ Принят',
    in_progress: '🔄 В работе',
    testing: '🧪 Тестирование',
    completed: '🎉 Завершен',
    cancelled: '❌ Отменен',
    on_hold: '⏸️ Приостановлен',
  }
  return names[status] || status
}

const calculateProgress = (status: string) => {
  const progress: Record<string, number> = {
    new: 10,
    review: 25,
    accepted: 40,
    in_progress: 60,
    testing: 80,
    completed: 100,
    cancelled: 0,
    on_hold: 0,
  }
  return progress[status] || 0
}

const getInitials = (name: string) => {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const getPixelVariant = (status: string): 'default' | 'blue' | 'yellow' | 'pink' | 'green' | 'purple' => {
  const variants: Record<string, 'default' | 'blue' | 'yellow' | 'pink' | 'green' | 'purple'> = {
    new: 'blue',
    review: 'yellow',
    accepted: 'purple',
    in_progress: 'yellow',
    testing: 'green',
    completed: 'green',
    cancelled: 'pink',
    on_hold: 'default',
  }
  return variants[status] || 'default'
}

export const ProjectCard = ({
  project,
  onView,
  onEdit,
  onDelete,
  onArchive,
  onContact,
  onAddPayment,
  onComplete,
  onViewFiles,
  onAssignExecutor,
  onExecutorPayment,
}: ProjectCardProps) => {
  const progress = calculateProgress(project.status)
  const statusColor = getStatusColor(project.status)
  const statusName = getStatusName(project.status)
  const pixelVariant = getPixelVariant(project.status)

  return (
    <PixelCard variant={pixelVariant} className="bg-white rounded-2xl shadow-lg border-l-4 overflow-hidden hover:shadow-2xl transition-all duration-300 hover:-translate-y-1"
      style={{
        borderLeftColor:
          project.status === 'new'
            ? '#2196F3'
            : project.status === 'review'
            ? '#FF9800'
            : project.status === 'accepted'
            ? '#9C27B0'
            : project.status === 'in_progress'
            ? '#FFC107'
            : project.status === 'testing'
            ? '#4CAF50'
            : project.status === 'completed'
            ? '#66BB6A'
            : project.status === 'cancelled'
            ? '#f44336'
            : '#9E9E9E',
      }}
    >
      {/* Header with Status */}
      <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-5 py-4 flex items-center justify-between border-b border-gray-200">
        <div className={`px-4 py-2 rounded-xl bg-gradient-to-r ${statusColor} text-white text-sm font-semibold shadow-md`}>
          {statusName}
        </div>
        <div className="bg-gray-700 text-white px-3 py-1 rounded-lg text-xs font-bold">
          #{project.id}
        </div>
      </div>

      {/* Title */}
      <div className="px-5 py-4">
        <h3 className="text-lg font-bold text-gray-900 mb-1 line-clamp-2">{project.title}</h3>
        <span className="inline-block px-3 py-1 bg-gray-100 text-gray-700 rounded-lg text-xs font-semibold">
          {project.project_type || 'Не указано'}
        </span>
      </div>

      {/* Client Info */}
      <div className="px-5 py-3 bg-gray-50 border-y border-gray-200 flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-600 flex items-center justify-center text-white font-bold text-sm shadow-md">
          {getInitials(project.user?.first_name || 'U')}
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-semibold text-gray-900 text-sm truncate">
            {project.user?.first_name || 'Неизвестно'}
          </div>
          <div className="text-xs text-gray-500 truncate">@{project.user?.username || 'нет'}</div>
        </div>
      </div>

      {/* Executor Section */}
      {project.assigned_to ? (
        <div className="px-5 py-3 bg-amber-50 border-b border-amber-200">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-orange-400 to-red-600 flex items-center justify-center text-white font-bold text-xs shadow-md">
              {getInitials(project.assigned_to.username || 'E')}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs text-amber-700 font-semibold uppercase">Исполнитель</div>
              <div className="font-semibold text-gray-900 text-sm truncate">{project.assigned_to.username}</div>
            </div>
          </div>
          {/* Executor Payment Info */}
          {project.executor_cost && (
            <div className="mt-3 p-2 bg-white rounded-lg border border-amber-300">
              <div className="flex justify-between items-center text-xs">
                <span className="text-amber-700 font-medium">Выплаты:</span>
                <div>
                  <span className="text-orange-600 font-bold">{project.executor_paid_total?.toLocaleString() || 0}₽</span>
                  <span className="text-gray-500"> / {project.executor_cost?.toLocaleString() || 0}₽</span>
                </div>
              </div>
              {project.executor_cost && project.executor_paid_total && project.executor_cost > project.executor_paid_total && (
                <div className="text-xs text-amber-700 mt-1">
                  Осталось: <strong>{(project.executor_cost - project.executor_paid_total).toLocaleString()}₽</strong>
                </div>
              )}
            </div>
          )}
          {/* Executor Payment Button */}
          {onExecutorPayment && (
            <button
              onClick={() => onExecutorPayment(project.id)}
              className="w-full mt-3 px-3 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-all text-xs font-semibold flex items-center justify-center gap-2"
            >
              <Banknote className="w-3 h-3" />
              Оплата исполнителю
            </button>
          )}
        </div>
      ) : (
        <div className="px-5 py-3 border-b border-gray-200">
          <button
            onClick={() => onAssignExecutor?.(project.id)}
            className="w-full px-3 py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-purple-500 hover:text-purple-600 transition-all text-sm font-semibold flex items-center justify-center gap-2"
          >
            <UserPlus className="w-4 h-4" />
            Назначить исполнителя
          </button>
        </div>
      )}

      {/* Stats */}
      <div className="px-5 py-4 grid grid-cols-2 gap-3">
        <div className="text-center">
          <div className="text-xs text-gray-500 mb-1">Сложность</div>
          <div className="text-sm font-bold text-gray-900">
            {project.complexity === 'simple'
              ? '🟢 Простой'
              : project.complexity === 'medium'
              ? '🟡 Средний'
              : project.complexity === 'complex'
              ? '🟠 Сложный'
              : project.complexity === 'premium'
              ? '🔴 Премиум'
              : project.complexity}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-500 mb-1">Стоимость</div>
          <div className="text-lg font-bold text-purple-600">{project.estimated_cost?.toLocaleString() || 0}₽</div>
        </div>
      </div>

      {/* Progress */}
      <div className="px-5 py-3 bg-gray-50">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs font-semibold text-gray-600 uppercase">Прогресс</span>
          <span className="text-xs font-bold text-purple-600">{progress}%</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full bg-gradient-to-r ${statusColor} transition-all duration-500 rounded-full`}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Payments Section */}
      <div className="px-5 py-3 bg-yellow-50 border-t border-yellow-200">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs font-semibold text-yellow-700 uppercase">Оплаты</span>
          <div className="text-sm">
            <span className="font-bold text-green-600">{project.client_paid_total?.toLocaleString() || 0}₽</span>
            <span className="text-gray-500"> / {project.estimated_cost?.toLocaleString() || 0}₽</span>
          </div>
        </div>
        {project.payments && project.payments.length > 0 && (
          <div className="space-y-1 mb-2">
            {project.payments.slice(-3).map((payment: any, idx: number) => (
              <div key={idx} className="flex justify-between text-xs bg-white p-2 rounded border border-yellow-300">
                <span className="text-gray-600">{payment.payment_type || 'Оплата'}</span>
                <div>
                  <span className="text-green-600 font-bold">+{payment.amount?.toLocaleString()}₽</span>
                  <span className="text-gray-400 ml-2">{payment.payment_date?.slice(0, 10)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
        <button
          onClick={() => onAddPayment(project.id)}
          className="w-full px-3 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-all text-xs font-semibold flex items-center justify-center gap-2"
        >
          <DollarSign className="w-3 h-3" />
          Добавить оплату
        </button>
      </div>

      {/* Deadline */}
      {project.deadline && (
        <div className="px-5 py-2 bg-orange-50 border-t border-orange-200 flex items-center gap-2">
          <span className="text-xs text-orange-700">📅 Дедлайн:</span>
          <span className="text-xs font-bold text-orange-900">{project.deadline.slice(0, 10)}</span>
        </div>
      )}

      {/* Actions */}
      <div className="px-5 py-4 bg-gray-50 border-t border-gray-200 flex gap-2 flex-wrap">
        <button
          onClick={() => onView(project.id)}
          className="flex-1 min-w-[80px] px-3 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-all text-xs font-semibold flex items-center justify-center gap-1"
        >
          <Eye className="w-3 h-3" />
          Просмотр
        </button>
        <button
          onClick={() => onEdit(project.id)}
          className="flex-1 min-w-[80px] px-3 py-2 bg-cyan-100 text-cyan-700 rounded-lg hover:bg-cyan-200 transition-all text-xs font-semibold flex items-center justify-center gap-1"
        >
          <Edit className="w-3 h-3" />
          Редактировать
        </button>
        {(project.status === 'testing' || project.status === 'in_progress') && onComplete && (
          <button
            onClick={() => onComplete(project.id)}
            className="flex-1 min-w-[80px] px-3 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-all text-xs font-semibold flex items-center justify-center gap-1"
          >
            <CheckCircle className="w-3 h-3" />
            Завершить
          </button>
        )}
        {project.chat && (
          <button className="flex-1 min-w-[80px] px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-all text-xs font-semibold flex items-center justify-center gap-1">
            <MessageCircle className="w-3 h-3" />
            Чат
          </button>
        )}
        {project.user?.telegram_id && (
          <button
            onClick={() => onContact(project.user.telegram_id)}
            className="flex-1 min-w-[80px] px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-all text-xs font-semibold flex items-center justify-center gap-1"
          >
            <MessageCircle className="w-3 h-3" />
            Связаться
          </button>
        )}
        {onViewFiles && (
          <button
            onClick={() => onViewFiles(project.id)}
            className="flex-1 min-w-[80px] px-3 py-2 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-all text-xs font-semibold flex items-center justify-center gap-1"
          >
            <File className="w-3 h-3" />
            Файлы
          </button>
        )}
        <button
          onClick={() => onArchive(project.id)}
          className="flex-1 min-w-[80px] px-3 py-2 bg-amber-100 text-amber-700 rounded-lg hover:bg-amber-200 transition-all text-xs font-semibold flex items-center justify-center gap-1"
        >
          <Archive className="w-3 h-3" />
          {project.is_archived ? 'Восстановить' : 'Архив'}
        </button>
        <button
          onClick={() => onDelete(project.id)}
          className="flex-1 min-w-[80px] px-3 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-all text-xs font-semibold flex items-center justify-center gap-1"
        >
          <Trash2 className="w-3 h-3" />
          Удалить
        </button>
      </div>

      {/* Footer */}
      <div className="px-5 py-2 bg-gray-100 border-t border-gray-200 flex items-center gap-2 text-xs text-gray-500">
        <span>🕐 Создан:</span>
        <span className="font-medium">{project.created_at?.slice(0, 10)}</span>
      </div>
    </PixelCard>
  )
}
