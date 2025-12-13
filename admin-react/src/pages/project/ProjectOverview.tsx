/**
 * Вкладка "Обзор" проекта
 * Показывает общую информацию, прогресс, карточки клиента и команды
 */

import { useState, useEffect } from 'react'
import { useOutletContext, useNavigate } from 'react-router-dom'
import {
  Users, Calendar, TrendingUp, Clock, User, Activity as ActivityIcon,
  Mail, Phone, DollarSign, CheckSquare, MessageSquare, AlertCircle
} from 'lucide-react'
import axiosInstance from '../../services/api'

interface Project {
  id: number
  title: string
  description?: string
  status: string
  progress?: number
  client_name?: string
  budget?: number
  deadline?: string
  created_at?: string
  estimated_cost?: number
  executor_cost?: number
  final_cost?: number
  user?: {
    id: number
    username: string
    first_name?: string
    last_name?: string
    phone?: string
    email?: string
  }
  assigned_to?: {
    id: number
    username: string
    first_name?: string
    last_name?: string
  }
  assigned_executor?: {
    id: number
    username: string
    first_name?: string
    last_name?: string
  }
}

interface OutletContext {
  project: Project
}

interface Task {
  id: number
  title: string
  status: string
  priority: string
  deadline?: string
  comments_count?: number
}

interface Payment {
  id: number
  type: string
  amount: number
  status: string
  due_date?: string
}

interface Activity {
  id: number
  action: string
  user_name: string
  created_at: string
  details?: string
}

export const ProjectOverview = () => {
  const { project } = useOutletContext<OutletContext>()
  const navigate = useNavigate()
  const [activities, setActivities] = useState<Activity[]>([])
  const [loadingActivity, setLoadingActivity] = useState(false)
  const [recentTasks, setRecentTasks] = useState<Task[]>([])
  const [loadingTasks, setLoadingTasks] = useState(false)
  const [recentPayments, setRecentPayments] = useState<Payment[]>([])
  const [loadingPayments, setLoadingPayments] = useState(false)

  // Загрузка активности проекта
  useEffect(() => {
    const loadActivity = async () => {
      try {
        setLoadingActivity(true)
        // TODO: Реализовать endpoint для получения активности проекта
        // const response = await axiosInstance.get(`/admin/api/projects/${project.id}/activity`)
        // setActivities(response.data.activities || [])

        // Временные моковые данные
        setActivities([
          {
            id: 1,
            action: 'create',
            user_name: 'admin',
            created_at: project.created_at || new Date().toISOString(),
            details: 'Проект создан'
          }
        ])
      } catch (error) {
        console.error('Error loading activity:', error)
      } finally {
        setLoadingActivity(false)
      }
    }

    loadActivity()
  }, [project.id])

  // Загрузка последних задач
  useEffect(() => {
    const loadRecentTasks = async () => {
      try {
        setLoadingTasks(true)
        const response = await axiosInstance.get(`/admin/api/projects/${project.id}/tasks`)
        if (response.data.success) {
          const tasks = response.data.tasks || []
          // Показываем только последние 5 задач в работе или новые
          const activeTasks = tasks
            .filter((t: Task) => t.status === 'in_progress' || t.status === 'pending' || t.status === 'new')
            .slice(0, 5)
          setRecentTasks(activeTasks)
        }
      } catch (error) {
        console.error('Error loading tasks:', error)
      } finally {
        setLoadingTasks(false)
      }
    }

    loadRecentTasks()
  }, [project.id])

  // Загрузка последних платежей
  useEffect(() => {
    const loadRecentPayments = async () => {
      try {
        setLoadingPayments(true)
        const response = await axiosInstance.get(`/admin/api/projects/${project.id}/payments`)
        if (response.data.success) {
          const payments = response.data.payments || []
          // Показываем последние 3 платежа
          setRecentPayments(payments.slice(0, 3))
        }
      } catch (error) {
        console.error('Error loading payments:', error)
      } finally {
        setLoadingPayments(false)
      }
    }

    loadRecentPayments()
  }, [project.id])

  // Форматирование даты для активности
  const formatActivityDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days === 0) return 'Сегодня'
    if (days === 1) return 'Вчера'
    if (days < 7) return `${days} дней назад`
    return date.toLocaleDateString('ru-RU')
  }

  // Статусы задач
  const taskStatuses: Record<string, { label: string; color: string }> = {
    pending: { label: 'Ожидает', color: 'gray' },
    new: { label: 'Новая', color: 'blue' },
    in_progress: { label: 'В работе', color: 'yellow' },
    review: { label: 'На проверке', color: 'purple' },
    completed: { label: 'Завершена', color: 'green' },
  }

  const getTaskStatus = (status: string) => {
    return taskStatuses[status] || taskStatuses.pending
  }

  // Типы платежей
  const paymentTypes: Record<string, string> = {
    PREPAYMENT: 'Предоплата',
    MILESTONE: 'Этап',
    FINAL: 'Финальный',
    ADDITIONAL: 'Дополнительный',
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900 dark:text-white">Обзор проекта</h2>

      {/* Быстрые карточки */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500 rounded-lg">
              <TrendingUp className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-blue-600 dark:text-blue-400">Прогресс</p>
              <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">{project.progress || 0}%</p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg p-4 border border-green-200 dark:border-green-800">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500 rounded-lg">
              <Users className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-green-600 dark:text-green-400">Клиент</p>
              <p className="text-lg font-bold text-green-900 dark:text-green-100 truncate">
                {project.client_name || project.user?.username || 'Не указан'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500 rounded-lg">
              <Calendar className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-purple-600 dark:text-purple-400">Дедлайн</p>
              <p className="text-lg font-bold text-purple-900 dark:text-purple-100">
                {project.deadline
                  ? new Date(project.deadline).toLocaleDateString('ru-RU')
                  : 'Не установлен'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-lg p-4 border border-orange-200 dark:border-orange-800">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-500 rounded-lg">
              <Clock className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-orange-600 dark:text-orange-400">Создан</p>
              <p className="text-lg font-bold text-orange-900 dark:text-orange-100">
                {project.created_at
                  ? new Date(project.created_at).toLocaleDateString('ru-RU')
                  : 'Недавно'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Финансовая информация */}
      {(project.estimated_cost || project.executor_cost || project.final_cost) && (
        <div className="bg-gradient-to-br from-emerald-50 to-green-100 dark:from-emerald-900/20 dark:to-green-800/20 rounded-lg p-6 border border-emerald-200 dark:border-emerald-800">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-emerald-500 rounded-lg">
              <DollarSign className="w-5 h-5 text-white" />
            </div>
            <h3 className="text-lg font-semibold text-emerald-900 dark:text-emerald-100">Финансы проекта</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {project.estimated_cost && (
              <div>
                <p className="text-sm text-emerald-600 dark:text-emerald-400">Оценочная стоимость</p>
                <p className="text-xl font-bold text-emerald-900 dark:text-emerald-100">
                  {project.estimated_cost.toLocaleString('ru-RU')} ₽
                </p>
              </div>
            )}
            {project.executor_cost && (
              <div>
                <p className="text-sm text-emerald-600 dark:text-emerald-400">Стоимость исполнителя</p>
                <p className="text-xl font-bold text-emerald-900 dark:text-emerald-100">
                  {project.executor_cost.toLocaleString('ru-RU')} ₽
                </p>
              </div>
            )}
            {project.final_cost && (
              <div>
                <p className="text-sm text-emerald-600 dark:text-emerald-400">Итоговая стоимость</p>
                <p className="text-xl font-bold text-emerald-900 dark:text-emerald-100">
                  {project.final_cost.toLocaleString('ru-RU')} ₽
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Описание */}
      {project.description && (
        <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Описание проекта</h3>
          <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{project.description}</p>
        </div>
      )}

      {/* Команда, Последние задачи и Платежи */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Команда проекта */}
        <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-4">
            <Users className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Команда проекта</h3>
          </div>

          <div className="space-y-4">
            {/* Клиент */}
            {project.user && (
              <div className="flex items-start gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-full">
                  <User className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">Клиент</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                    {project.user.first_name || project.user.username}
                  </p>
                  {project.user.phone && (
                    <div className="flex items-center gap-1 mt-1">
                      <Phone className="w-3 h-3 text-gray-400" />
                      <p className="text-xs text-gray-500 dark:text-gray-400">{project.user.phone}</p>
                    </div>
                  )}
                  {project.user.email && (
                    <div className="flex items-center gap-1 mt-1">
                      <Mail className="w-3 h-3 text-gray-400" />
                      <p className="text-xs text-gray-500 dark:text-gray-400">{project.user.email}</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Исполнитель */}
            {(project.assigned_executor || project.assigned_to) && (
              <div className="flex items-start gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-full">
                  <User className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">Исполнитель</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                    {(project.assigned_executor?.first_name || project.assigned_executor?.username) ||
                     (project.assigned_to?.first_name || project.assigned_to?.username)}
                  </p>
                </div>
              </div>
            )}

            {!project.user && !project.assigned_executor && !project.assigned_to && (
              <p className="text-gray-500 dark:text-gray-400 text-sm text-center py-4">
                Команда не назначена
              </p>
            )}
          </div>
        </div>

        {/* Последние задачи */}
        <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <CheckSquare className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Задачи в работе</h3>
            </div>
            <button
              onClick={() => navigate(`/projects/${project.id}/tasks`)}
              className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
              Все задачи →
            </button>
          </div>

          {loadingTasks ? (
            <p className="text-gray-500 dark:text-gray-400 text-sm text-center py-4">Загрузка...</p>
          ) : recentTasks.length > 0 ? (
            <div className="space-y-2">
              {recentTasks.map((task) => {
                const statusInfo = getTaskStatus(task.status)
                return (
                  <div
                    key={task.id}
                    onClick={() => navigate(`/projects/${project.id}/tasks`)}
                    className="flex items-start gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 cursor-pointer transition-colors"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {task.title}
                        </p>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          statusInfo.color === 'yellow' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' :
                          statusInfo.color === 'blue' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' :
                          'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400'
                        }`}>
                          {statusInfo.label}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                        {task.deadline && (
                          <span>{new Date(task.deadline).toLocaleDateString('ru-RU')}</span>
                        )}
                        {task.comments_count !== undefined && task.comments_count > 0 && (
                          <div className="flex items-center gap-1">
                            <MessageSquare className="w-3 h-3" />
                            <span>{task.comments_count}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400 text-sm text-center py-4">
              Нет активных задач
            </p>
          )}
        </div>
      </div>

      {/* Последние платежи и Активность */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Последние платежи */}
        <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Последние платежи</h3>
            </div>
            <button
              onClick={() => navigate(`/projects/${project.id}/finance`)}
              className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
              Все платежи →
            </button>
          </div>

          {loadingPayments ? (
            <p className="text-gray-500 dark:text-gray-400 text-sm text-center py-4">Загрузка...</p>
          ) : recentPayments.length > 0 ? (
            <div className="space-y-2">
              {recentPayments.map((payment) => (
                <div
                  key={payment.id}
                  onClick={() => navigate(`/projects/${project.id}/finance`)}
                  className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-emerald-300 dark:hover:border-emerald-600 cursor-pointer transition-colors"
                >
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {paymentTypes[payment.type] || payment.type}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {payment.due_date && new Date(payment.due_date).toLocaleDateString('ru-RU')}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-gray-900 dark:text-white">
                      {payment.amount.toLocaleString('ru-RU')} ₽
                    </p>
                    <span className={`text-xs ${
                      payment.status === 'PAID' ? 'text-green-600 dark:text-green-400' : 'text-yellow-600 dark:text-yellow-400'
                    }`}>
                      {payment.status === 'PAID' ? 'Оплачен' : 'Ожидает'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400 text-sm text-center py-4">
              Нет платежей
            </p>
          )}
        </div>

        {/* Последняя активность */}
        <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-4">
            <ActivityIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Последняя активность</h3>
          </div>

          {loadingActivity ? (
            <p className="text-gray-500 dark:text-gray-400 text-sm text-center py-4">Загрузка...</p>
          ) : activities.length > 0 ? (
            <div className="space-y-3">
              {activities.slice(0, 5).map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-start gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900 dark:text-white">
                      <span className="font-medium">{activity.user_name}</span>
                      {' '}
                      <span className="text-gray-600 dark:text-gray-400">{activity.details}</span>
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {formatActivityDate(activity.created_at)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400 text-sm text-center py-4">
              Нет активности
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default ProjectOverview
