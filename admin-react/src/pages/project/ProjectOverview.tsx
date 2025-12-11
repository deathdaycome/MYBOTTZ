/**
 * Вкладка "Обзор" проекта
 * Показывает общую информацию, прогресс, карточки клиента и команды
 */

import { useState, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import { Users, Calendar, TrendingUp, Clock, User, Activity as ActivityIcon, Mail, Phone, DollarSign } from 'lucide-react'
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

interface Activity {
  id: number
  action: string
  user_name: string
  created_at: string
  details?: string
}

export const ProjectOverview = () => {
  const { project } = useOutletContext<OutletContext>()
  const [activities, setActivities] = useState<Activity[]>([])
  const [loadingActivity, setLoadingActivity] = useState(false)

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

      {/* Команда и Активность */}
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
