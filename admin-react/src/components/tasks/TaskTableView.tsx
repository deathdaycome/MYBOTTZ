/**
 * Табличное представление задач
 * Отображение задач и правок в виде таблицы
 */

import { Calendar, User, Eye, Edit2, Trash2, RotateCcw, CheckSquare, Clock, AlertCircle } from 'lucide-react'
import type { Task } from '../../api/tasks'

interface TaskTableViewProps {
  tasks: Task[]
  onView: (task: Task) => void
  onEdit: (task: Task) => void
  onDelete: (taskId: number) => void
}

export const TaskTableView = ({ tasks, onView, onEdit, onDelete }: TaskTableViewProps) => {
  // Иконки статусов
  const statusIcons: Record<string, any> = {
    pending: AlertCircle,
    in_progress: Clock,
    completed: CheckSquare,
  }

  // Цвета статусов
  const statusColors: Record<string, string> = {
    pending: 'blue',
    in_progress: 'yellow',
    completed: 'green',
  }

  // Лейблы статусов
  const statusLabels: Record<string, string> = {
    pending: 'Новая',
    in_progress: 'В работе',
    completed: 'Завершена',
  }

  // Цвета приоритетов
  const priorityColors: Record<string, string> = {
    low: 'gray',
    normal: 'blue',
    high: 'orange',
    urgent: 'red',
  }

  // Лейблы приоритетов
  const priorityLabels: Record<string, string> = {
    low: 'Низкий',
    normal: 'Обычный',
    high: 'Высокий',
    urgent: 'Срочный',
  }

  const getStatusIcon = (status: string) => {
    return statusIcons[status] || AlertCircle
  }

  const getStatusColor = (status: string) => {
    return statusColors[status] || 'gray'
  }

  const getStatusLabel = (status: string) => {
    return statusLabels[status] || status
  }

  const getPriorityColor = (priority: string) => {
    return priorityColors[priority] || 'gray'
  }

  const getPriorityLabel = (priority: string) => {
    return priorityLabels[priority] || priority
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-700">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
                Тип
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
                Название
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
                Проект
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
                Статус
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
                Приоритет
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
                Исполнитель
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
                Дедлайн
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {tasks.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-12 text-center">
                  <div className="flex flex-col items-center">
                    <CheckSquare className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-3" />
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                      Задачи не найдены
                    </p>
                  </div>
                </td>
              </tr>
            ) : (
              tasks.map((task) => {
                const StatusIcon = getStatusIcon(task.status)
                const statusColor = getStatusColor(task.status)
                const priorityColor = getPriorityColor(task.priority)

                return (
                  <tr
                    key={task.id}
                    className="hover:bg-gray-50 dark:hover:bg-gray-900/30 transition-colors cursor-pointer"
                    onClick={() => onView(task)}
                  >
                    {/* Тип */}
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        {task.type === 'REVISION' ? (
                          <div className="flex items-center gap-1 px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 rounded-md text-xs font-medium">
                            <RotateCcw className="w-3 h-3" />
                            <span>Правка</span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-1 px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-md text-xs font-medium">
                            <CheckSquare className="w-3 h-3" />
                            <span>Задача</span>
                          </div>
                        )}
                        {task.created_from_chat && (
                          <span className="px-1.5 py-0.5 bg-sky-100 dark:bg-sky-900/30 text-sky-700 dark:text-sky-400 rounded text-xs">
                            Чат
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Название */}
                    <td className="px-4 py-4">
                      <div className="flex flex-col">
                        <p className="text-sm font-medium text-gray-900 dark:text-white line-clamp-1">
                          {task.title}
                        </p>
                        {task.description && (
                          <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-1 mt-0.5">
                            {task.description}
                          </p>
                        )}
                      </div>
                    </td>

                    {/* Проект */}
                    <td className="px-4 py-4 whitespace-nowrap">
                      {task.project ? (
                        <span className="text-sm text-gray-700 dark:text-gray-300">
                          {task.project.title}
                        </span>
                      ) : (
                        <span className="text-sm text-gray-400">—</span>
                      )}
                    </td>

                    {/* Статус */}
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-${statusColor}-100 dark:bg-${statusColor}-900/30 text-${statusColor}-700 dark:text-${statusColor}-400`}>
                        <StatusIcon className="w-3.5 h-3.5" />
                        <span className="text-xs font-medium">{getStatusLabel(task.status)}</span>
                      </div>
                    </td>

                    {/* Приоритет */}
                    <td className="px-4 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-${priorityColor}-100 dark:bg-${priorityColor}-900/30 text-${priorityColor}-700 dark:text-${priorityColor}-400`}>
                        {getPriorityLabel(task.priority)}
                      </span>
                    </td>

                    {/* Исполнитель */}
                    <td className="px-4 py-4 whitespace-nowrap">
                      {task.assigned_to ? (
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold">
                            {(task.assigned_to.first_name || task.assigned_to.username).charAt(0).toUpperCase()}
                          </div>
                          <div className="flex flex-col">
                            <span className="text-sm text-gray-900 dark:text-white">
                              {task.assigned_to.first_name && task.assigned_to.last_name
                                ? `${task.assigned_to.first_name} ${task.assigned_to.last_name}`
                                : task.assigned_to.username}
                            </span>
                          </div>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">Не назначен</span>
                      )}
                    </td>

                    {/* Дедлайн */}
                    <td className="px-4 py-4 whitespace-nowrap">
                      {task.deadline ? (
                        <div className="flex items-center gap-1.5 text-sm">
                          <Calendar className="w-3.5 h-3.5 text-gray-400" />
                          <span className={task.is_overdue ? 'text-red-600 dark:text-red-400 font-medium' : 'text-gray-700 dark:text-gray-300'}>
                            {new Date(task.deadline).toLocaleDateString('ru-RU')}
                          </span>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">—</span>
                      )}
                    </td>

                    {/* Действия */}
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => onView(task)}
                          className="p-1.5 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded transition-colors"
                          title="Просмотр"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => onEdit(task)}
                          className="p-1.5 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                          title="Редактировать"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => onDelete(task.id)}
                          className="p-1.5 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded transition-colors"
                          title="Удалить"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default TaskTableView
