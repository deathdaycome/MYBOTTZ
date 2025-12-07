import { useState, useEffect } from 'react'
import { Plus, CheckCircle, Clock, AlertCircle, Filter } from 'lucide-react'

interface Task {
  id: number
  title: string
  description: string
  status: string
  priority: string
  deadline: string | null
  assigned_to: string | null
  created_at: string
}

interface ProjectTasksTabProps {
  projectId: number
  onCountChange?: (count: number) => void
  onRefresh?: () => void
}

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    new: 'bg-blue-100 text-blue-700',
    in_progress: 'bg-yellow-100 text-yellow-700',
    review: 'bg-purple-100 text-purple-700',
    completed: 'bg-green-100 text-green-700',
    cancelled: 'bg-red-100 text-red-700',
  }
  return colors[status] || 'bg-gray-100 text-gray-700'
}

const getStatusName = (status: string) => {
  const names: Record<string, string> = {
    new: 'Новая',
    in_progress: 'В работе',
    review: 'На проверке',
    completed: 'Завершена',
    cancelled: 'Отменена',
  }
  return names[status] || status
}

const getPriorityIcon = (priority: string) => {
  const icons: Record<string, string> = {
    low: '🔵',
    medium: '🟡',
    high: '🟠',
    urgent: '🔴',
  }
  return icons[priority] || '⚪'
}

export const ProjectTasksTab = ({ projectId, onCountChange, onRefresh }: ProjectTasksTabProps) => {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all') // all, active, completed

  useEffect(() => {
    loadTasks()
  }, [projectId])

  const loadTasks = async () => {
    try {
      setLoading(true)
      // TODO: Реальный запрос к API
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/tasks`,
        {
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        const tasksList = data.tasks || []
        setTasks(tasksList)
        if (onCountChange) {
          onCountChange(tasksList.length)
        }
      } else {
        setTasks([])
        if (onCountChange) {
          onCountChange(0)
        }
      }
    } catch (err) {
      console.error('Ошибка загрузки задач:', err)
      setTasks([])
      if (onCountChange) {
        onCountChange(0)
      }
    } finally {
      setLoading(false)
    }
  }

  const filteredTasks = tasks.filter((task) => {
    if (filter === 'active') return task.status !== 'completed' && task.status !== 'cancelled'
    if (filter === 'completed') return task.status === 'completed'
    return true
  })

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-900">Задачи проекта</h3>
        <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all font-medium shadow-md">
          <Plus className="w-4 h-4" />
          Создать задачу
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2 mb-4">
        <Filter className="w-4 h-4 text-gray-500" />
        <button
          onClick={() => setFilter('all')}
          className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
            filter === 'all'
              ? 'bg-purple-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Все ({tasks.length})
        </button>
        <button
          onClick={() => setFilter('active')}
          className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
            filter === 'active'
              ? 'bg-purple-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Активные ({tasks.filter((t) => t.status !== 'completed' && t.status !== 'cancelled').length})
        </button>
        <button
          onClick={() => setFilter('completed')}
          className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
            filter === 'completed'
              ? 'bg-purple-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Завершённые ({tasks.filter((t) => t.status === 'completed').length})
        </button>
      </div>

      {/* Tasks List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        </div>
      ) : filteredTasks.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">Задачи не найдены</p>
          <p className="text-gray-400 text-sm mt-1">Создайте первую задачу для этого проекта</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredTasks.map((task) => (
            <div
              key={task.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span>{getPriorityIcon(task.priority)}</span>
                    <h4 className="font-semibold text-gray-900">{task.title}</h4>
                  </div>
                  {task.description && (
                    <p className="text-sm text-gray-600 line-clamp-2">{task.description}</p>
                  )}
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(task.status)}`}>
                  {getStatusName(task.status)}
                </span>
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                {task.assigned_to && (
                  <span className="flex items-center gap-1">
                    👤 {task.assigned_to}
                  </span>
                )}
                {task.deadline && (
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {new Date(task.deadline).toLocaleDateString('ru-RU')}
                  </span>
                )}
                <span className="text-xs text-gray-400">
                  #{task.id}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
