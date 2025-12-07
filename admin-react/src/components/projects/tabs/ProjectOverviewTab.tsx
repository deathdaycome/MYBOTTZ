import { Edit, User, Calendar, Clock, DollarSign, Layers, AlertCircle, TrendingUp, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'

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
  final_cost: number
  estimated_hours: number
  actual_hours: number
  client_paid_total: number
  executor_paid_total: number
  deadline: string | null
  created_at: string
  updated_at: string
  stage?: string
  progress?: number
  user: {
    id: number
    first_name: string
    username: string
  } | null
  assigned_to: {
    id: number
    username: string
  } | null
  technical_requirements: string | null
  additional_requirements: string | null
}

interface ProjectOverviewTabProps {
  project: Project
  onEdit?: (id: number) => void
}

const getComplexityName = (complexity: string) => {
  const names: Record<string, string> = {
    simple: '🟢 Простой',
    medium: '🟡 Средний',
    complex: '🟠 Сложный',
    premium: '🔴 Премиум',
  }
  return names[complexity] || complexity
}

const getPriorityName = (priority: string) => {
  const names: Record<string, string> = {
    low: '🔵 Низкий',
    medium: '🟡 Средний',
    high: '🟠 Высокий',
    urgent: '🔴 Срочный',
  }
  return names[priority] || priority
}

const getTypeName = (type: string) => {
  const names: Record<string, string> = {
    telegram_bot: '🤖 Telegram бот',
    web_app: '🌐 Веб-приложение',
    mobile_app: '📱 Мобильное приложение',
    integration: '🔌 Интеграция',
    automation: '⚙️ Автоматизация',
    consulting: '💡 Консультация',
    other: '📦 Другое',
  }
  return names[type] || type
}

export const ProjectOverviewTab = ({ project, onEdit }: ProjectOverviewTabProps) => {
  const [isTZExpanded, setIsTZExpanded] = useState(false)

  const formatTechnicalSpecification = () => {
    const parts = []
    if (project.description) parts.push(project.description)
    if (project.technical_requirements)
      parts.push('**Технические требования:**\n' + project.technical_requirements)
    if (project.additional_requirements)
      parts.push('**Дополнительные требования:**\n' + project.additional_requirements)
    return parts.join('\n\n') || 'Описание отсутствует'
  }

  const tz = formatTechnicalSpecification()

  // Расчёт рентабельности
  const profit = project.estimated_cost - project.executor_cost
  const profitMargin = project.estimated_cost > 0 ? ((profit / project.estimated_cost) * 100).toFixed(1) : 0

  return (
    <div className="p-6 space-y-6">
      {/* Кнопка редактирования */}
      {onEdit && (
        <div className="flex justify-end">
          <button
            onClick={() => onEdit(project.id)}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all font-medium shadow-md"
          >
            <Edit className="w-4 h-4" />
            Редактировать проект
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Левая колонка - Основная информация */}
        <div className="lg:col-span-2 space-y-6">
          {/* Техническое задание */}
          <div className="bg-white border-l-4 border-blue-500 rounded-lg shadow-md overflow-hidden">
            <div className="bg-gray-50 px-4 py-3 flex items-center justify-between border-b border-gray-200">
              <div className="flex items-center gap-2">
                <Layers className="w-5 h-5 text-blue-600" />
                <strong className="text-gray-800">Техническое задание</strong>
              </div>
              <button
                onClick={() => setIsTZExpanded(!isTZExpanded)}
                className="text-blue-600 hover:text-blue-700 transition-colors p-1"
              >
                {isTZExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
              </button>
            </div>
            <div
              className={`px-4 py-3 text-gray-700 whitespace-pre-wrap transition-all ${
                isTZExpanded ? '' : 'max-h-32 overflow-hidden'
              }`}
            >
              {tz}
            </div>
            {!isTZExpanded && tz.length > 200 && (
              <div className="px-4 py-2 bg-gradient-to-t from-gray-50 to-transparent">
                <button
                  onClick={() => setIsTZExpanded(true)}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  Показать полностью...
                </button>
              </div>
            )}
          </div>

          {/* Основные параметры */}
          <div className="bg-white border border-gray-200 rounded-lg shadow-md p-4">
            <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-indigo-600" />
              Основные параметры
            </h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Тип проекта</p>
                <p className="font-medium text-gray-900">{getTypeName(project.project_type)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Сложность</p>
                <p className="font-medium text-gray-900">{getComplexityName(project.complexity)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Приоритет</p>
                <p className="font-medium text-gray-900">{getPriorityName(project.priority)}</p>
              </div>
              {project.stage && (
                <div>
                  <p className="text-sm text-gray-500">Этап</p>
                  <p className="font-medium text-gray-900">{project.stage}</p>
                </div>
              )}
            </div>
          </div>

          {/* Временные рамки */}
          <div className="bg-white border border-gray-200 rounded-lg shadow-md p-4">
            <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <Clock className="w-5 h-5 text-green-600" />
              Временные рамки
            </h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Создан</p>
                <p className="font-medium text-gray-900">
                  {new Date(project.created_at).toLocaleDateString('ru-RU')}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Обновлён</p>
                <p className="font-medium text-gray-900">
                  {new Date(project.updated_at).toLocaleDateString('ru-RU')}
                </p>
              </div>
              {project.deadline && (
                <>
                  <div>
                    <p className="text-sm text-gray-500">Дедлайн</p>
                    <p className="font-medium text-gray-900">
                      {new Date(project.deadline).toLocaleDateString('ru-RU')}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Осталось дней</p>
                    <p className="font-medium text-gray-900">
                      {Math.ceil((new Date(project.deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))}
                    </p>
                  </div>
                </>
              )}
              {project.estimated_hours > 0 && (
                <>
                  <div>
                    <p className="text-sm text-gray-500">Оценка часов</p>
                    <p className="font-medium text-gray-900">{project.estimated_hours} ч</p>
                  </div>
                  {project.actual_hours > 0 && (
                    <div>
                      <p className="text-sm text-gray-500">Фактически</p>
                      <p className="font-medium text-gray-900">{project.actual_hours} ч</p>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>

        {/* Правая колонка - Участники и финансы */}
        <div className="space-y-6">
          {/* Участники */}
          <div className="bg-white border border-gray-200 rounded-lg shadow-md p-4">
            <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <User className="w-5 h-5 text-purple-600" />
              Участники
            </h4>
            <div className="space-y-3">
              {project.user && (
                <div>
                  <p className="text-sm text-gray-500 mb-1">Клиент</p>
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white text-sm font-semibold">
                      {project.user.first_name?.charAt(0) || 'К'}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{project.user.first_name || project.user.username}</p>
                      <p className="text-xs text-gray-500">@{project.user.username}</p>
                    </div>
                  </div>
                </div>
              )}
              {project.assigned_to && (
                <div>
                  <p className="text-sm text-gray-500 mb-1">Исполнитель</p>
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center text-white text-sm font-semibold">
                      {project.assigned_to.username?.charAt(0).toUpperCase() || 'И'}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">@{project.assigned_to.username}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Финансы */}
          <div className="bg-white border border-gray-200 rounded-lg shadow-md p-4">
            <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-emerald-600" />
              Финансы
            </h4>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">Стоимость клиента</p>
                <p className="text-lg font-bold text-gray-900">{project.estimated_cost.toLocaleString('ru-RU')} ₽</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Стоимость исполнителя</p>
                <p className="text-lg font-bold text-gray-900">{project.executor_cost.toLocaleString('ru-RU')} ₽</p>
              </div>
              <div className="pt-2 border-t border-gray-200">
                <p className="text-sm text-gray-500">Прибыль</p>
                <div className="flex items-baseline gap-2">
                  <p className={`text-lg font-bold ${profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {profit.toLocaleString('ru-RU')} ₽
                  </p>
                  <span className="text-sm text-gray-500">({profitMargin}%)</span>
                </div>
              </div>
              {project.client_paid_total > 0 && (
                <div>
                  <p className="text-sm text-gray-500">Оплачено клиентом</p>
                  <p className="text-lg font-bold text-blue-600">
                    {project.client_paid_total.toLocaleString('ru-RU')} ₽
                  </p>
                </div>
              )}
              {project.executor_paid_total > 0 && (
                <div>
                  <p className="text-sm text-gray-500">Выплачено исполнителю</p>
                  <p className="text-lg font-bold text-orange-600">
                    {project.executor_paid_total.toLocaleString('ru-RU')} ₽
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Прогресс */}
          {project.progress !== undefined && project.progress >= 0 && (
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-lg shadow-md p-4">
              <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-600" />
                Прогресс выполнения
              </h4>
              <div className="flex items-center justify-center">
                <div className="relative w-32 h-32">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle
                      cx="64"
                      cy="64"
                      r="56"
                      stroke="#e5e7eb"
                      strokeWidth="12"
                      fill="none"
                    />
                    <circle
                      cx="64"
                      cy="64"
                      r="56"
                      stroke="url(#gradient)"
                      strokeWidth="12"
                      fill="none"
                      strokeDasharray={`${2 * Math.PI * 56}`}
                      strokeDashoffset={`${2 * Math.PI * 56 * (1 - project.progress / 100)}`}
                      strokeLinecap="round"
                      className="transition-all duration-500"
                    />
                    <defs>
                      <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#9333ea" />
                        <stop offset="100%" stopColor="#ec4899" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-3xl font-bold text-gray-900">{project.progress}%</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
