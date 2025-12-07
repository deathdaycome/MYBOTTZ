import { X } from 'lucide-react'

interface Employee {
  id: number
  name: string
  username: string
  role: string
}

interface Project {
  id: number
  title: string
  status?: string
}

interface TaskFiltersProps {
  filters: {
    status?: string
    priority?: string
    assigned_to_id?: number
    created_by_id?: number
    type?: string
    project_id?: number
  }
  onFilterChange: (filters: any) => void
  onClose: () => void
  employees: Employee[]
  projects?: Project[]
}

export const TaskFilters = ({ filters, onFilterChange, onClose, employees, projects = [] }: TaskFiltersProps) => {
  const handleFilterChange = (key: string, value: any) => {
    onFilterChange({
      ...filters,
      [key]: value || undefined,
    })
  }

  const handleReset = () => {
    onFilterChange({})
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">Фильтры</h3>
        <button
          onClick={onClose}
          className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {/* Type filter */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Тип</label>
          <select
            value={filters.type || ''}
            onChange={(e) => handleFilterChange('type', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">Все типы</option>
            <option value="TASK">Задачи</option>
            <option value="REVISION">Правки</option>
          </select>
        </div>

        {/* Status filter */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Статус</label>
          <select
            value={filters.status || ''}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">Все статусы</option>
            <option value="pending">Новые</option>
            <option value="in_progress">В работе</option>
            <option value="completed">Завершенные</option>
          </select>
        </div>

        {/* Priority filter */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Приоритет</label>
          <select
            value={filters.priority || ''}
            onChange={(e) => handleFilterChange('priority', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">Все приоритеты</option>
            <option value="urgent">Срочный</option>
            <option value="high">Высокий</option>
            <option value="normal">Обычный</option>
            <option value="low">Низкий</option>
          </select>
        </div>

        {/* Project filter */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Проект</label>
          <select
            value={filters.project_id || ''}
            onChange={(e) =>
              handleFilterChange('project_id', e.target.value ? parseInt(e.target.value) : null)
            }
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">Все проекты</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.title}
              </option>
            ))}
          </select>
        </div>

        {/* Assigned to filter */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Исполнитель</label>
          <select
            value={filters.assigned_to_id || ''}
            onChange={(e) =>
              handleFilterChange('assigned_to_id', e.target.value ? parseInt(e.target.value) : null)
            }
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">Все исполнители</option>
            {employees.map((emp) => (
              <option key={emp.id} value={emp.id}>
                {emp.name} (@{emp.username})
              </option>
            ))}
          </select>
        </div>

        {/* Created by filter */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Создатель</label>
          <select
            value={filters.created_by_id || ''}
            onChange={(e) =>
              handleFilterChange('created_by_id', e.target.value ? parseInt(e.target.value) : null)
            }
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">Все создатели</option>
            {employees.map((emp) => (
              <option key={emp.id} value={emp.id}>
                {emp.name} (@{emp.username})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Reset button */}
      <div className="mt-4 flex justify-end">
        <button
          onClick={handleReset}
          className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 font-medium transition-colors"
        >
          Сбросить фильтры
        </button>
      </div>
    </div>
  )
}
