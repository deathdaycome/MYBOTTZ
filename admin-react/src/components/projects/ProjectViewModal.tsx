import { useState, useEffect, useRef } from 'react'
import {
  X,
  Edit,
  FileText,
  CheckCircle,
  Layers,
  DollarSign,
  Calendar,
  Clock,
  User,
  MessageCircle,
  Copy,
  ChevronDown,
  ChevronUp,
  BarChart3,
} from 'lucide-react'

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
  is_archived: boolean
  created_at: string
  updated_at: string
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
  project_metadata: {
    test_link: string | null
    bot_token: string | null
    bot_username: string | null
    telegram_channel_id: string | null
    timeweb_login: string | null
    timeweb_password: string | null
    timeweb_server_id: string | null
  } | null
  technical_requirements: string | null
  additional_requirements: string | null
}

interface ProjectViewModalProps {
  isOpen: boolean
  onClose: () => void
  onEdit: (id: number) => void
  onContact: (telegramId: number) => void
  project: Project | null
}

// Helper functions
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

const getInitials = (name: string) => {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const copyToClipboard = async (text: string, label: string) => {
  try {
    await navigator.clipboard.writeText(text)
    alert(`${label} скопировано в буфер обмена`)
  } catch (err) {
    alert('Ошибка копирования')
  }
}

export const ProjectViewModal = ({ isOpen, onClose, onEdit, onContact, project }: ProjectViewModalProps) => {
  const [isTZExpanded, setIsTZExpanded] = useState(false)
  const modalContentRef = useRef<HTMLDivElement>(null)

  // Block body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      const scrollY = window.scrollY
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'
      document.body.style.overflow = 'hidden'

      // Reset modal content scroll to top
      if (modalContentRef.current) {
        modalContentRef.current.scrollTop = 0
      }
    } else {
      const scrollY = document.body.style.top
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      document.body.style.overflow = ''
      window.scrollTo(0, parseInt(scrollY || '0') * -1)
    }
    return () => {
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      document.body.style.overflow = ''
    }
  }, [isOpen])

  if (!isOpen || !project) return null

  const progress = calculateProgress(project.status)
  const statusColor = getStatusColor(project.status)
  const statusName = getStatusName(project.status)

  // Format technical specification
  const formatTechnicalSpecification = () => {
    const parts = []
    if (project.description) parts.push(project.description)
    if (project.technical_requirements) parts.push('**Технические требования:**\n' + project.technical_requirements)
    if (project.additional_requirements) parts.push('**Дополнительные требования:**\n' + project.additional_requirements)
    return parts.join('\n\n') || 'Описание отсутствует'
  }

  return (
    <>
      <style>{`
        .modal-content-scrollable {
          scrollbar-width: none !important;
          -ms-overflow-style: none !important;
        }
        .modal-content-scrollable::-webkit-scrollbar {
          display: none !important;
          width: 0 !important;
          height: 0 !important;
        }
      `}</style>
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-2"
        style={{ overflow: 'hidden' }}
      >
        <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full max-h-[95vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-3 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold">{project.title}</h3>
              <p className="text-purple-100 text-xs mt-0.5">Проект #{project.id} • {statusName}</p>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="text-white hover:bg-white/20 rounded-lg p-1.5 transition-colors flex-shrink-0"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Body - Scrollable */}
        <div ref={modalContentRef} className="modal-content-scrollable px-4 py-3 overflow-y-auto flex-1">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Left Column - Main Content */}
            <div className="lg:col-span-2 space-y-3">
              {/* Technical Specification */}
              <div className="bg-white border-l-4 border-blue-500 rounded-lg shadow-md overflow-hidden">
                <div className="bg-gray-50 px-4 py-3 flex items-center justify-between border-b border-gray-200">
                  <div className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-blue-600" />
                    <strong className="text-gray-800">Техническое задание</strong>
                  </div>
                  <button
                    type="button"
                    onClick={() => setIsTZExpanded(!isTZExpanded)}
                    className="text-blue-600 hover:text-blue-700 flex items-center gap-1 text-sm font-semibold"
                  >
                    {isTZExpanded ? (
                      <>
                        <ChevronUp className="w-4 h-4" />
                        Свернуть
                      </>
                    ) : (
                      <>
                        <ChevronDown className="w-4 h-4" />
                        Развернуть
                      </>
                    )}
                  </button>
                </div>
                <div
                  className={`px-4 py-3 bg-white transition-all duration-300 ${
                    isTZExpanded ? 'max-h-none' : 'max-h-[200px] overflow-hidden'
                  }`}
                >
                  <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
                    {formatTechnicalSpecification()}
                  </div>
                </div>
              </div>

              {/* Info Cards Grid */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {/* Status */}
                <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-4 h-4 text-gray-500" />
                    <div className="text-xs text-gray-500 font-semibold uppercase">Статус</div>
                  </div>
                  <div className={`px-3 py-1.5 rounded-lg bg-gradient-to-r ${statusColor} text-white text-sm font-bold inline-block`}>
                    {statusName}
                  </div>
                </div>

                {/* Complexity */}
                <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
                  <div className="flex items-center gap-2 mb-2">
                    <Layers className="w-4 h-4 text-gray-500" />
                    <div className="text-xs text-gray-500 font-semibold uppercase">Сложность</div>
                  </div>
                  <div className="text-sm font-bold text-gray-900">{getComplexityName(project.complexity)}</div>
                </div>

                {/* Priority */}
                <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
                  <div className="flex items-center gap-2 mb-2">
                    <BarChart3 className="w-4 h-4 text-gray-500" />
                    <div className="text-xs text-gray-500 font-semibold uppercase">Приоритет</div>
                  </div>
                  <div className="text-sm font-bold text-gray-900">{getPriorityName(project.priority)}</div>
                </div>

                {/* Cost */}
                <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
                  <div className="flex items-center gap-2 mb-2">
                    <DollarSign className="w-4 h-4 text-gray-500" />
                    <div className="text-xs text-gray-500 font-semibold uppercase">Стоимость</div>
                  </div>
                  <div className="text-lg font-bold text-purple-600">{project.estimated_cost?.toLocaleString() || 0}₽</div>
                </div>

                {/* Final Cost */}
                {project.final_cost && (
                  <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
                    <div className="flex items-center gap-2 mb-2">
                      <DollarSign className="w-4 h-4 text-gray-500" />
                      <div className="text-xs text-gray-500 font-semibold uppercase">Итоговая стоимость</div>
                    </div>
                    <div className="text-lg font-bold text-green-600">{project.final_cost.toLocaleString()}₽</div>
                  </div>
                )}

                {/* Created Date */}
                <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar className="w-4 h-4 text-gray-500" />
                    <div className="text-xs text-gray-500 font-semibold uppercase">Дата создания</div>
                  </div>
                  <div className="text-sm font-bold text-gray-900">{project.created_at?.slice(0, 10)}</div>
                </div>

                {/* Project Type */}
                <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="w-4 h-4 text-gray-500" />
                    <div className="text-xs text-gray-500 font-semibold uppercase">Тип проекта</div>
                  </div>
                  <div className="text-sm font-bold text-gray-900">{project.project_type || 'Не указано'}</div>
                </div>

                {/* Deadline */}
                {project.deadline && (
                  <div className="bg-white rounded-lg shadow-md p-4 border border-orange-200 bg-orange-50">
                    <div className="flex items-center gap-2 mb-2">
                      <Calendar className="w-4 h-4 text-orange-600" />
                      <div className="text-xs text-orange-700 font-semibold uppercase">Дедлайн</div>
                    </div>
                    <div className="text-sm font-bold text-orange-900">{project.deadline.slice(0, 10)}</div>
                  </div>
                )}

                {/* Estimated Hours */}
                {project.estimated_hours && (
                  <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Clock className="w-4 h-4 text-gray-500" />
                      <div className="text-xs text-gray-500 font-semibold uppercase">Оценка часов</div>
                    </div>
                    <div className="text-sm font-bold text-gray-900">{project.estimated_hours}ч</div>
                  </div>
                )}

                {/* Actual Hours */}
                {project.actual_hours && (
                  <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
                    <div className="flex items-center gap-2 mb-2">
                      <Clock className="w-4 h-4 text-gray-500" />
                      <div className="text-xs text-gray-500 font-semibold uppercase">Фактически часов</div>
                    </div>
                    <div className="text-sm font-bold text-gray-900">{project.actual_hours}ч</div>
                  </div>
                )}
              </div>

              {/* Executor Info */}
              {project.assigned_to && (
                <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-lg shadow-md p-5 border border-orange-200">
                  <div className="flex items-center gap-2 mb-3">
                    <User className="w-5 h-5 text-orange-600" />
                    <h4 className="text-sm font-bold text-gray-800 uppercase">Исполнитель</h4>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-orange-400 to-red-600 flex items-center justify-center text-white font-bold text-sm shadow-md">
                      {getInitials(project.assigned_to.username || 'E')}
                    </div>
                    <div>
                      <div className="font-bold text-gray-900">{project.assigned_to.username}</div>
                      <div className="text-xs text-gray-600">ID: {project.assigned_to.id}</div>
                    </div>
                  </div>
                  {project.executor_cost && (
                    <div className="mt-3 p-3 bg-white rounded-lg border border-orange-300">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm text-orange-700 font-semibold">Выплаты исполнителю:</span>
                        <div>
                          <span className="text-orange-600 font-bold">{project.executor_paid_total?.toLocaleString() || 0}₽</span>
                          <span className="text-gray-500"> / {project.executor_cost?.toLocaleString() || 0}₽</span>
                        </div>
                      </div>
                      {project.executor_cost > (project.executor_paid_total || 0) && (
                        <div className="text-sm text-amber-700">
                          Осталось: <strong>{(project.executor_cost - (project.executor_paid_total || 0)).toLocaleString()}₽</strong>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Client Info */}
              {project.user && (
                <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg shadow-md p-5 border border-purple-200">
                  <div className="flex items-center gap-2 mb-3">
                    <User className="w-5 h-5 text-purple-600" />
                    <h4 className="text-sm font-bold text-gray-800 uppercase">Клиент</h4>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-pink-600 flex items-center justify-center text-white font-bold text-sm shadow-md">
                        {getInitials(project.user.first_name || 'U')}
                      </div>
                      <div>
                        <div className="font-bold text-gray-900">{project.user.first_name || 'Неизвестно'}</div>
                        <div className="text-sm text-gray-600">@{project.user.username || 'нет'}</div>
                        <div className="text-xs text-gray-500">Telegram ID: {project.user.telegram_id}</div>
                      </div>
                    </div>
                    {project.user.telegram_id && (
                      <button
                        onClick={() => onContact(project.user.telegram_id)}
                        className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-all text-sm font-semibold flex items-center gap-2"
                      >
                        <MessageCircle className="w-4 h-4" />
                        Связаться
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* Technical Information */}
              {project.project_metadata && (
                <div className="bg-gray-50 rounded-lg shadow-md p-5 border border-gray-300">
                  <h4 className="text-sm font-bold text-gray-800 uppercase mb-3">Техническая информация</h4>
                  <div className="space-y-2">
                    {project.project_metadata.bot_token && (
                      <div className="flex items-center justify-between bg-white p-3 rounded-lg border border-gray-200">
                        <div>
                          <div className="text-xs text-gray-500 font-semibold">Bot Token</div>
                          <div className="text-sm font-mono text-gray-900">{project.project_metadata.bot_token.slice(0, 20)}...</div>
                        </div>
                        <button
                          onClick={() => copyToClipboard(project.project_metadata!.bot_token!, 'Bot Token')}
                          className="text-blue-600 hover:text-blue-700 p-2"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                    {project.project_metadata.bot_username && (
                      <div className="flex items-center justify-between bg-white p-3 rounded-lg border border-gray-200">
                        <div>
                          <div className="text-xs text-gray-500 font-semibold">Bot Username</div>
                          <div className="text-sm font-mono text-gray-900">@{project.project_metadata.bot_username}</div>
                        </div>
                        <button
                          onClick={() => copyToClipboard(project.project_metadata!.bot_username!, 'Bot Username')}
                          className="text-blue-600 hover:text-blue-700 p-2"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                    {project.project_metadata.telegram_channel_id && (
                      <div className="flex items-center justify-between bg-white p-3 rounded-lg border border-gray-200">
                        <div>
                          <div className="text-xs text-gray-500 font-semibold">Telegram Channel ID</div>
                          <div className="text-sm font-mono text-gray-900">{project.project_metadata.telegram_channel_id}</div>
                        </div>
                        <button
                          onClick={() => copyToClipboard(project.project_metadata!.telegram_channel_id!, 'Channel ID')}
                          className="text-blue-600 hover:text-blue-700 p-2"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                    {project.project_metadata.timeweb_login && (
                      <div className="flex items-center justify-between bg-white p-3 rounded-lg border border-gray-200">
                        <div>
                          <div className="text-xs text-gray-500 font-semibold">Timeweb Login</div>
                          <div className="text-sm font-mono text-gray-900">{project.project_metadata.timeweb_login}</div>
                        </div>
                        <button
                          onClick={() => copyToClipboard(project.project_metadata!.timeweb_login!, 'Timeweb Login')}
                          className="text-blue-600 hover:text-blue-700 p-2"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                    {project.project_metadata.timeweb_password && (
                      <div className="flex items-center justify-between bg-white p-3 rounded-lg border border-gray-200">
                        <div>
                          <div className="text-xs text-gray-500 font-semibold">Timeweb Password</div>
                          <div className="text-sm font-mono text-gray-900">••••••••</div>
                        </div>
                        <button
                          onClick={() => copyToClipboard(project.project_metadata!.timeweb_password!, 'Timeweb Password')}
                          className="text-blue-600 hover:text-blue-700 p-2"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                    {project.project_metadata.test_link && (
                      <div className="flex items-center justify-between bg-white p-3 rounded-lg border border-gray-200">
                        <div className="flex-1">
                          <div className="text-xs text-gray-500 font-semibold">Тестовая ссылка</div>
                          <a
                            href={project.project_metadata.test_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:underline break-all"
                          >
                            {project.project_metadata.test_link}
                          </a>
                        </div>
                        <button
                          onClick={() => copyToClipboard(project.project_metadata!.test_link!, 'Тестовая ссылка')}
                          className="text-blue-600 hover:text-blue-700 p-2"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Right Column - Progress & Actions */}
            <div className="space-y-3">
              {/* Progress Card */}
              <div className="bg-white rounded-lg shadow-md p-5 border border-gray-200">
                <h4 className="text-sm font-bold text-gray-800 uppercase mb-4 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-purple-600" />
                  Прогресс проекта
                </h4>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-semibold text-gray-600">Выполнено</span>
                    <span className="text-2xl font-bold text-purple-600">{progress}%</span>
                  </div>
                  <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full bg-gradient-to-r ${statusColor} transition-all duration-500 rounded-full`}
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <div className={`px-4 py-2 rounded-lg bg-gradient-to-r ${statusColor} text-white text-center font-bold text-sm`}>
                    {statusName}
                  </div>
                </div>
              </div>

              {/* Financial Summary */}
              <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-lg shadow-md p-5 border border-yellow-200">
                <h4 className="text-sm font-bold text-gray-800 uppercase mb-3">Финансы</h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Стоимость проекта:</span>
                    <span className="text-lg font-bold text-purple-600">{project.estimated_cost?.toLocaleString() || 0}₽</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Оплачено клиентом:</span>
                    <span className="text-lg font-bold text-green-600">{project.client_paid_total?.toLocaleString() || 0}₽</span>
                  </div>
                  <div className="flex justify-between items-center pt-2 border-t border-yellow-300">
                    <span className="text-sm text-gray-600">Остаток к оплате:</span>
                    <span className="text-lg font-bold text-orange-600">
                      {((project.estimated_cost || 0) - (project.client_paid_total || 0)).toLocaleString()}₽
                    </span>
                  </div>
                </div>
              </div>

              {/* Payments History */}
              {project.payments && project.payments.length > 0 && (
                <div className="bg-white rounded-lg shadow-md p-5 border border-gray-200">
                  <h4 className="text-sm font-bold text-gray-800 uppercase mb-3">История оплат</h4>
                  <div className="space-y-2 max-h-[300px] overflow-y-auto">
                    {project.payments.map((payment: any, idx: number) => (
                      <div key={idx} className="flex justify-between items-center bg-gray-50 p-3 rounded-lg border border-gray-200">
                        <div>
                          <div className="text-sm font-semibold text-gray-900">{payment.payment_type || 'Оплата'}</div>
                          <div className="text-xs text-gray-500">{payment.payment_date?.slice(0, 10)}</div>
                        </div>
                        <div className="text-lg font-bold text-green-600">+{payment.amount?.toLocaleString()}₽</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-4 py-2.5 bg-gray-50 border-t border-gray-200 flex gap-2 flex-shrink-0">
          <button
            type="button"
            onClick={() => onEdit(project.id)}
            className="flex-1 px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-lg hover:from-cyan-700 hover:to-blue-700 transition-all font-semibold flex items-center justify-center gap-2 text-sm"
          >
            <Edit className="w-4 h-4" />
            Редактировать
          </button>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold text-sm"
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
    </>
  )
}
