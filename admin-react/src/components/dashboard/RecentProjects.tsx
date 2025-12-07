import { useState } from 'react'
import { FolderKanban, Eye, Edit } from 'lucide-react'
import { formatDate } from '../../utils/formatters'

interface Project {
  id: number
  name: string
  client: string
  status: string
  created_at: string
}

interface RecentProjectsProps {
  projects?: Project[]
  onUpdateStatus?: (projectId: number) => void
}

export const RecentProjects = ({ projects, onUpdateStatus }: RecentProjectsProps) => {
  const defaultProjects: Project[] = projects || [
    {
      id: 1,
      name: 'Сайт для компании ABC',
      client: 'Иван Иванов',
      status: 'in_progress',
      created_at: new Date().toISOString(),
    },
    {
      id: 2,
      name: 'Мобильное приложение XYZ',
      client: 'Мария Петрова',
      status: 'new',
      created_at: new Date(Date.now() - 86400000).toISOString(),
    },
    {
      id: 3,
      name: 'Редизайн портала',
      client: 'Алексей Смирнов',
      status: 'testing',
      created_at: new Date(Date.now() - 172800000).toISOString(),
    },
  ]

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<
      string,
      { label: string; className: string }
    > = {
      new: { label: 'Новый', className: 'bg-blue-100 text-blue-700' },
      review: { label: 'На рассмотрении', className: 'bg-yellow-100 text-yellow-700' },
      accepted: { label: 'Принят', className: 'bg-green-100 text-green-700' },
      in_progress: { label: 'В работе', className: 'bg-purple-100 text-purple-700' },
      testing: { label: 'Тестирование', className: 'bg-indigo-100 text-indigo-700' },
      completed: { label: 'Завершен', className: 'bg-green-100 text-green-700' },
      cancelled: { label: 'Отменен', className: 'bg-red-100 text-red-700' },
    }

    const config = statusConfig[status] || { label: status, className: 'bg-gray-100 text-gray-700' }
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${config.className}`}>
        {config.label}
      </span>
    )
  }

  const handleViewProject = (projectId: number) => {
    window.location.href = `/admin/projects/${projectId}/detail`
  }

  return (
    <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
      <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
        <FolderKanban className="w-5 h-5 text-purple-600" />
        Недавние проекты
      </h3>

      {defaultProjects.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <FolderKanban className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>Нет проектов</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                  Проект
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                  Клиент
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                  Статус
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                  Дата
                </th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody>
              {defaultProjects.map((project) => (
                <tr
                  key={project.id}
                  className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                >
                  <td className="py-3 px-4">
                    <div className="font-semibold text-gray-900">{project.name}</div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="text-gray-700">{project.client}</div>
                  </td>
                  <td className="py-3 px-4">{getStatusBadge(project.status)}</td>
                  <td className="py-3 px-4">
                    <div className="text-sm text-gray-600">
                      {formatDate(project.created_at, { month: 'short', day: 'numeric' })}
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => handleViewProject(project.id)}
                        className="p-2 rounded-lg hover:bg-blue-50 text-blue-600 transition-colors"
                        title="Просмотр"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => onUpdateStatus && onUpdateStatus(project.id)}
                        className="p-2 rounded-lg hover:bg-purple-50 text-purple-600 transition-colors"
                        title="Изменить статус"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
