/**
 * Основной компонент просмотра проекта с вкладками
 * Согласно ТЗ: карточка проекта - центр интерфейса
 */

import { useState, useEffect } from 'react'
import { useParams, useNavigate, Outlet, NavLink } from 'react-router-dom'
import {
  Home,
  CheckSquare,
  RotateCcw,
  MessageSquare,
  FileText,
  DollarSign,
  Server,
  ArrowLeft,
  Loader2,
} from 'lucide-react'
import axiosInstance from '../services/api'

interface Project {
  id: number
  title: string
  description?: string
  status: string
  progress: number
  client_name?: string
  budget?: number
  deadline?: string
  created_at?: string
}

export const ProjectView = () => {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Загрузка данных проекта
  useEffect(() => {
    const loadProject = async () => {
      if (!projectId) return

      try {
        setLoading(true)
        const response = await axiosInstance.get(`/admin/api/projects/${projectId}`)
        setProject(response.data)
        setError(null)
      } catch (err: any) {
        console.error('Error loading project:', err)
        setError('Ошибка загрузки проекта')
      } finally {
        setLoading(false)
      }
    }

    loadProject()
  }, [projectId])

  // Конфигурация вкладок
  const tabs = [
    { id: 'overview', label: 'Обзор', icon: Home, path: `/projects/${projectId}/overview` },
    { id: 'tasks', label: 'Задачи', icon: CheckSquare, path: `/projects/${projectId}/tasks` },
    { id: 'revisions', label: 'Правки', icon: RotateCcw, path: `/projects/${projectId}/revisions` },
    { id: 'chat', label: 'Чат', icon: MessageSquare, path: `/projects/${projectId}/chat` },
    { id: 'documents', label: 'Документы', icon: FileText, path: `/projects/${projectId}/documents` },
    { id: 'finance', label: 'Финансы', icon: DollarSign, path: `/projects/${projectId}/finance` },
    { id: 'hosting', label: 'Хостинг', icon: Server, path: `/projects/${projectId}/hosting` },
  ]

  // Состояния проекта с цветами
  const statusColors: Record<string, string> = {
    new: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    in_progress: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    testing: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
    completed: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    archived: 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
  }

  const statusLabels: Record<string, string> = {
    new: 'Новый',
    in_progress: 'В работе',
    testing: 'Тестирование',
    completed: 'Завершен',
    archived: 'Архивирован',
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-4">
        <p className="text-red-500 dark:text-red-400">{error || 'Проект не найден'}</p>
        <button
          onClick={() => navigate('/projects')}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          Вернуться к проектам
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Шапка проекта */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        {/* Навигация назад и статус */}
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <button
            onClick={() => navigate('/projects')}
            className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Все проекты</span>
          </button>

          <span
            className={`px-3 py-1 rounded-full text-xs font-medium ${
              statusColors[project.status] || statusColors.new
            }`}
          >
            {statusLabels[project.status] || project.status}
          </span>
        </div>

        {/* Информация о проекте */}
        <div className="px-6 py-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{project.title}</h1>
          {project.description && (
            <p className="text-gray-600 dark:text-gray-400 mb-4">{project.description}</p>
          )}

          {/* Прогресс */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Прогресс</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {project.progress || 0}%
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${project.progress || 0}%` }}
              ></div>
            </div>
          </div>

          {/* Дополнительная информация */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            {project.client_name && (
              <div>
                <span className="text-gray-500 dark:text-gray-400">Клиент:</span>
                <span className="ml-2 text-gray-900 dark:text-white">{project.client_name}</span>
              </div>
            )}
            {project.budget && (
              <div>
                <span className="text-gray-500 dark:text-gray-400">Бюджет:</span>
                <span className="ml-2 text-gray-900 dark:text-white">
                  {project.budget.toLocaleString('ru-RU')} ₽
                </span>
              </div>
            )}
            {project.deadline && (
              <div>
                <span className="text-gray-500 dark:text-gray-400">Дедлайн:</span>
                <span className="ml-2 text-gray-900 dark:text-white">
                  {new Date(project.deadline).toLocaleDateString('ru-RU')}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Вкладки навигации */}
        <div className="border-t border-gray-200 dark:border-gray-700">
          <nav className="flex overflow-x-auto scrollbar-hide">
            {tabs.map((tab) => (
              <NavLink
                key={tab.id}
                to={tab.path}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-6 py-4 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                    isActive
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:border-gray-300 dark:hover:border-gray-600'
                  }`
                }
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </NavLink>
            ))}
          </nav>
        </div>
      </div>

      {/* Контент вкладки */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <Outlet context={{ project }} />
      </div>
    </div>
  )
}

export default ProjectView
