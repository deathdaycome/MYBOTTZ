/**
 * Вкладка "Обзор" проекта
 * Показывает общую информацию, прогресс, карточки клиента и команды
 */

import { useOutletContext } from 'react-router-dom'
import { Users, Calendar, TrendingUp, Clock } from 'lucide-react'

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

interface OutletContext {
  project: Project
}

export const ProjectOverview = () => {
  const { project } = useOutletContext<OutletContext>()

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
              <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">{project.progress}%</p>
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
                {project.client_name || 'Не указан'}
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

      {/* Описание */}
      {project.description && (
        <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Описание проекта</h3>
          <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{project.description}</p>
        </div>
      )}

      {/* Placeholder для будущих секций */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Команда проекта</h3>
          <p className="text-gray-500 dark:text-gray-400 text-sm">Информация о команде будет добавлена</p>
        </div>

        <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Последняя активность</h3>
          <p className="text-gray-500 dark:text-gray-400 text-sm">История активности будет добавлена</p>
        </div>
      </div>
    </div>
  )
}

export default ProjectOverview
