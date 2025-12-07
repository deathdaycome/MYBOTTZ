/**
 * Вкладка "Правки" проекта
 * Список правок (задач с type=REVISION)
 */

import { useState, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import { RotateCcw, Plus, Loader2, Calendar, User, AlertCircle, Clock, CheckCircle2, XCircle } from 'lucide-react'
import axiosInstance from '../../services/api'

interface Project {
  id: number
  title: string
}

interface Revision {
  id: number
  title: string
  description?: string
  status: string
  priority: string
  assigned_to?: number
  assigned_to_name?: string
  deadline?: string
  created_at: string
  type: string
  created_from_chat?: boolean
}

interface OutletContext {
  project: Project
}

export const ProjectRevisions = () => {
  const { project } = useOutletContext<OutletContext>()
  const [revisions, setRevisions] = useState<Revision[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('all')

  // Загрузка правок
  useEffect(() => {
    loadRevisions()
  }, [project.id])

  const loadRevisions = async () => {
    try {
      setLoading(true)
      const response = await axiosInstance.get(`/admin/api/projects/${project.id}/revisions`)

      if (response.data.success) {
        // Берем только правки (type=REVISION)
        const projectRevisions = (response.data.revisions || []).filter(
          (item: Revision) => item.type === 'REVISION'
        )
        setRevisions(projectRevisions)
      }
      setError(null)
    } catch (err: any) {
      console.error('Error loading revisions:', err)
      setError('Ошибка загрузки правок')
    } finally {
      setLoading(false)
    }
  }

  // Статусы правок
  const revisionStatuses: Record<string, { label: string; color: string; icon: any }> = {
    new: { label: 'Новая', color: 'blue', icon: AlertCircle },
    in_progress: { label: 'В работе', color: 'yellow', icon: Clock },
    review: { label: 'На проверке', color: 'purple', icon: RotateCcw },
    completed: { label: 'Завершена', color: 'green', icon: CheckCircle2 },
    rejected: { label: 'Отклонена', color: 'red', icon: XCircle },
  }

  // Приоритеты
  const priorities: Record<string, { label: string; color: string }> = {
    low: { label: 'Низкий', color: 'gray' },
    medium: { label: 'Средний', color: 'blue' },
    high: { label: 'Высокий', color: 'orange' },
    urgent: { label: 'Срочный', color: 'red' },
  }

  const getRevisionStatus = (status: string) => {
    return revisionStatuses[status] || revisionStatuses.new
  }

  const getPriority = (priority: string) => {
    return priorities[priority] || priorities.medium
  }

  // Фильтрация правок
  const filteredRevisions = revisions.filter((revision) => {
    if (statusFilter === 'all') return true
    return revision.status === statusFilter
  })

  // Подсчет правок по статусам
  const statusCounts = revisions.reduce((acc, revision) => {
    acc[revision.status] = (acc[revision.status] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Правки проекта</h2>
        <button className="flex items-center gap-2 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors">
          <Plus className="w-4 h-4" />
          <span>Создать правку</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Информация */}
      <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
        <p className="text-sm text-purple-700 dark:text-purple-300">
          <strong>Правки</strong> - это замечания и доработки от клиента. Они могут быть созданы вручную или
          автоматически из чата с клиентом.
        </p>
      </div>

      {/* Фильтры по статусам */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        <button
          onClick={() => setStatusFilter('all')}
          className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
            statusFilter === 'all'
              ? 'bg-purple-500 text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
          }`}
        >
          Все ({revisions.length})
        </button>

        {Object.entries(revisionStatuses).map(([status, info]) => (
          <button
            key={status}
            onClick={() => setStatusFilter(status)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              statusFilter === status
                ? `bg-${info.color}-500 text-white`
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
          >
            {info.label} ({statusCounts[status] || 0})
          </button>
        ))}
      </div>

      {/* Список правок */}
      {filteredRevisions.length > 0 ? (
        <div className="space-y-3">
          {filteredRevisions.map((revision) => {
            const statusInfo = getRevisionStatus(revision.status)
            const priorityInfo = getPriority(revision.priority)
            const StatusIcon = statusInfo.icon

            return (
              <div
                key={revision.id}
                className="bg-white dark:bg-gray-800 rounded-lg border-2 border-purple-200 dark:border-purple-800 p-4 hover:shadow-md transition-shadow cursor-pointer"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    <div className={`p-2 bg-${statusInfo.color}-100 dark:bg-${statusInfo.color}-900/20 rounded-lg mt-1`}>
                      <StatusIcon className={`w-5 h-5 text-${statusInfo.color}-600 dark:text-${statusInfo.color}-400`} />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2 flex-wrap">
                        <h3 className="text-base font-semibold text-gray-900 dark:text-white">
                          {revision.title}
                        </h3>
                        {revision.created_from_chat && (
                          <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
                            Из чата
                          </span>
                        )}
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-medium bg-${priorityInfo.color}-100 text-${priorityInfo.color}-700 dark:bg-${priorityInfo.color}-900/30 dark:text-${priorityInfo.color}-400`}
                        >
                          {priorityInfo.label}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-medium bg-${statusInfo.color}-100 text-${statusInfo.color}-700 dark:bg-${statusInfo.color}-900/30 dark:text-${statusInfo.color}-400`}
                        >
                          {statusInfo.label}
                        </span>
                      </div>

                      {revision.description && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
                          {revision.description}
                        </p>
                      )}

                      <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                        {revision.assigned_to_name && (
                          <div className="flex items-center gap-1">
                            <User className="w-3 h-3" />
                            <span>{revision.assigned_to_name}</span>
                          </div>
                        )}
                        {revision.deadline && (
                          <div className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            <span>{new Date(revision.deadline).toLocaleDateString('ru-RU')}</span>
                          </div>
                        )}
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          <span>Создана: {new Date(revision.created_at).toLocaleDateString('ru-RU')}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <RotateCcw className="w-16 h-16 text-gray-300 dark:text-gray-600 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {statusFilter === 'all' ? 'Правки не найдены' : 'Нет правок с таким статусом'}
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            {statusFilter === 'all'
              ? 'Правки от клиента будут отображаться здесь'
              : 'Попробуйте изменить фильтр'}
          </p>
          {statusFilter === 'all' && (
            <button className="flex items-center gap-2 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors">
              <Plus className="w-4 h-4" />
              <span>Создать правку</span>
            </button>
          )}
        </div>
      )}
    </div>
  )
}

export default ProjectRevisions
