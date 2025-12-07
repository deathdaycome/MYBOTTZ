import { useState, useEffect, useCallback } from 'react'
import { Plus, Filter, Archive, RefreshCw, Search, X, LayoutGrid, List } from 'lucide-react'
import tasksApi from '../api/tasks'
import type { Task, TaskStats } from '../api/tasks'
import { TaskCard } from '../components/tasks/TaskCard'
import { TaskTableView } from '../components/tasks/TaskTableView'
import { TaskCreateModal } from '../components/tasks/TaskCreateModal'
import { TaskEditModal } from '../components/tasks/TaskEditModal'
import { TaskViewModal } from '../components/tasks/TaskViewModal'
import { TaskFilters } from '../components/tasks/TaskFilters'
import { TaskStatsHeader } from '../components/tasks/TaskStatsHeader'
import { ToastContainer } from '../components/common/Toast'

interface Employee {
  id: number
  first_name?: string
  last_name?: string
  username: string
  role: string
}

interface Project {
  id: number
  title: string
  status?: string
}

interface TaskFiltersState {
  status?: string
  priority?: string
  assigned_to_id?: number
  created_by_id?: number
  type?: string
  project_id?: number
}

export const Tasks = () => {
  const [tasks, setTasks] = useState<Task[]>([])
  const [stats, setStats] = useState<TaskStats | null>(null)
  const [employees, setEmployees] = useState<Employee[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<TaskFiltersState>({})
  const [showFilters, setShowFilters] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [viewMode, setViewMode] = useState<'kanban' | 'table'>('kanban')

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showViewModal, setShowViewModal] = useState(false)
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [draggedTask, setDraggedTask] = useState<Task | null>(null)
  const [dragOverColumn, setDragOverColumn] = useState<number | null>(null)

  // Toast notifications
  const [toasts, setToasts] = useState<Array<{ id: string; message: string; type: 'success' | 'error' | 'info' | 'warning' }>>([])

  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') => {
    const id = Date.now().toString()
    setToasts((prev) => [...prev, { id, message, type }])
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }, [])

  // Load tasks
  const loadTasks = useCallback(async () => {
    try {
      setLoading(true)
      console.log('🔄 Requesting tasks with filters:', filters)
      const response = await tasksApi.getTasks(filters)
      console.log('📦 API Response:', response)
      console.log('📊 Response success:', response.success)
      console.log('📋 Response tasks:', response.tasks)
      console.log('🔢 Tasks length:', response.tasks?.length)

      if (response.success) {
        setTasks(response.tasks || [])
        console.log('✅ Tasks set to state:', response.tasks?.length || 0)
      } else {
        console.error('❌ API returned success=false:', response)
        setTasks([])
      }
    } catch (error) {
      console.error('💥 Error loading tasks:', error)
      console.error('💥 Error details:', JSON.stringify(error, null, 2))
      showToast('Ошибка загрузки задач', 'error')
      setTasks([])
    } finally {
      setLoading(false)
    }
  }, [filters, showToast])

  // Load statistics
  const loadStats = useCallback(async () => {
    try {
      const response = await tasksApi.getStats()
      if (response.success) {
        setStats(response.stats)
      }
    } catch (error) {
      console.error('Error loading stats:', error)
    }
  }, [])

  // Load executors
  const loadExecutors = useCallback(async () => {
    try {
      const executors = await tasksApi.getExecutors()
      setEmployees(executors)
    } catch (error) {
      console.error('Error loading executors:', error)
    }
  }, [])

  // Load projects
  const loadProjects = useCallback(async () => {
    try {
      const projectsList = await tasksApi.getProjects()
      setProjects(projectsList)
    } catch (error) {
      console.error('Error loading projects:', error)
    }
  }, [])

  useEffect(() => {
    loadTasks()
    loadStats()
    loadExecutors()
    loadProjects()
  }, [loadTasks, loadStats, loadExecutors, loadProjects])

  // Filter tasks by search query
  const filterTasksBySearch = (tasksToFilter: Task[]) => {
    if (!searchQuery.trim()) return tasksToFilter

    const query = searchQuery.toLowerCase()
    return tasksToFilter.filter((task) => {
      const titleMatch = task.title.toLowerCase().includes(query)
      const descriptionMatch = task.description?.toLowerCase().includes(query)
      const assignedToMatch = task.assigned_to?.first_name?.toLowerCase().includes(query) ||
                             task.assigned_to?.last_name?.toLowerCase().includes(query) ||
                             task.assigned_to?.username?.toLowerCase().includes(query)

      return titleMatch || descriptionMatch || assignedToMatch
    })
  }

  // Group tasks by employee
  const groupTasksByEmployee = () => {
    const grouped: Record<number, { employee: Employee; tasks: Task[] }> = {}

    // Filter tasks by search first
    const filteredTasks = filterTasksBySearch(tasks)

    console.log('=== GROUPING DEBUG ===')
    console.log('Total tasks:', tasks.length)
    console.log('Filtered tasks:', filteredTasks.length)
    console.log('Employees:', employees.length, employees.map(e => ({ id: e.id, username: e.username })))

    // Group all tasks by all executors
    employees.forEach((emp) => {
      grouped[emp.id] = {
        employee: emp,
        tasks: [],
      }
    })

    console.log('Grouped keys:', Object.keys(grouped))

    filteredTasks.forEach((task) => {
      console.log('Task', task.id, 'assigned_to_id:', task.assigned_to_id, 'exists in grouped:', !!grouped[task.assigned_to_id])
      if (task.assigned_to_id && grouped[task.assigned_to_id]) {
        grouped[task.assigned_to_id].tasks.push(task)
      }
    })

    console.log('Final grouped:', Object.entries(grouped).map(([id, data]) => ({ id, tasksCount: data.tasks.length })))
    console.log('=== END DEBUG ===')

    return grouped
  }

  // Handle drag start
  const handleDragStart = (task: Task) => (e: React.DragEvent<HTMLDivElement>) => {
    console.log('Drag start:', task.title)
    setDraggedTask(task)
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', task.id.toString())
  }

  // Handle drag over
  const handleDragOver = (employeeId: number) => (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
    setDragOverColumn(employeeId)
  }

  // Handle drag leave
  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    // Проверяем что мышь действительно покинула колонку, а не просто перешла на дочерний элемент
    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX
    const y = e.clientY

    if (x < rect.left || x >= rect.right || y < rect.top || y >= rect.bottom) {
      setDragOverColumn(null)
    }
  }

  // Handle drop
  const handleDrop = (newAssignedToId: number) => async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setDragOverColumn(null)

    console.log('Drop on employee:', newAssignedToId, 'dragged task:', draggedTask)

    if (!draggedTask) {
      console.log('No dragged task')
      return
    }

    // Don't do anything if dropped on the same executor
    if (draggedTask.assigned_to_id === newAssignedToId) {
      console.log('Dropped on same executor')
      setDraggedTask(null)
      return
    }

    console.log('Reassigning task...')
    try {
      const response = await tasksApi.reassignTask(draggedTask.id, newAssignedToId)
      console.log('Reassign response:', response)
      if (response.success) {
        showToast('Задача переназначена', 'success')
        loadTasks()
        loadStats()
      }
    } catch (error) {
      console.error('Error reassigning task:', error)
      showToast('Ошибка переназначения задачи', 'error')
    } finally {
      setDraggedTask(null)
    }
  }

  // Handle status change
  const handleStatusChange = async (taskId: number, newStatus: string) => {
    try {
      const response = await tasksApi.updateTaskStatus(taskId, newStatus)
      if (response.success) {
        showToast('Статус обновлен', 'success')
        loadTasks()
        loadStats()
      }
    } catch (error) {
      console.error('Error updating status:', error)
      showToast('Ошибка обновления статуса', 'error')
    }
  }

  // Handle task creation
  const handleCreateTask = () => {
    setShowCreateModal(false)
    loadTasks()
    loadStats()
  }

  // Handle task update
  const handleUpdateTask = () => {
    setShowEditModal(false)
    setSelectedTask(null)
    loadTasks()
    loadStats()
  }

  // Handle task delete (archive)
  const handleDeleteTask = async (taskId: number) => {
    if (!confirm('Задача будет перемещена в архив. Продолжить?')) return

    try {
      const response = await tasksApi.archiveTask(taskId)
      if (response.success) {
        showToast('Задача перемещена в архив', 'success')
        loadTasks()
        loadStats()
        setShowViewModal(false)
        setSelectedTask(null)
      }
    } catch (error) {
      console.error('Error archiving task:', error)
      showToast('Ошибка архивации задачи', 'error')
    }
  }

  // Handle task view
  const handleViewTask = (task: Task) => {
    setSelectedTask(task)
    setShowViewModal(true)
  }

  // Handle task edit
  const handleEditTask = (task: Task) => {
    setSelectedTask(task)
    setShowEditModal(true)
  }

  const groupedTasks = groupTasksByEmployee()

  return (
    <>
      <div className="px-6 py-4 pb-6 space-y-4">
        {/* Header */}
        <div className="space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Планировщик задач</h1>
              <p className="text-gray-600 mt-1">Управление задачами команды</p>
            </div>

            <div className="flex items-center gap-2">
            {/* Filter button */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-2.5 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all border border-gray-300 shadow-sm"
            >
              <Filter className="w-4 h-4" />
              <span className="font-medium">Фильтры</span>
            </button>

            {/* Archive button */}
            <button
              onClick={() => (window.location.href = '/tasks/archive')}
              className="flex items-center gap-2 px-4 py-2.5 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all border border-gray-300 shadow-sm"
            >
              <Archive className="w-4 h-4" />
              <span className="font-medium">Архив</span>
            </button>

            {/* View mode toggle */}
            <div className="flex items-center bg-white border border-gray-300 rounded-lg shadow-sm">
              <button
                onClick={() => setViewMode('kanban')}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-l-lg transition-all ${
                  viewMode === 'kanban'
                    ? 'bg-blue-500 text-white'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
                title="Kanban доска"
              >
                <LayoutGrid className="w-4 h-4" />
                <span className="font-medium">Kanban</span>
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-r-lg transition-all ${
                  viewMode === 'table'
                    ? 'bg-blue-500 text-white'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
                title="Табличный вид"
              >
                <List className="w-4 h-4" />
                <span className="font-medium">Таблица</span>
              </button>
            </div>

            {/* Refresh button */}
            <button
              onClick={() => {
                loadTasks()
                loadStats()
              }}
              className="p-2.5 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-all border border-gray-300 shadow-sm"
              title="Обновить"
            >
              <RefreshCw className="w-4 h-4" />
            </button>

            {/* Create task button */}
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-md font-semibold"
            >
              <Plus className="w-5 h-5" />
              Создать задачу
            </button>
          </div>
          </div>

          {/* Search bar */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="🔍 Поиск задач по названию, описанию или исполнителю..."
              className="block w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
                title="Очистить"
              >
                <X className="h-5 w-5" />
              </button>
            )}
            {searchQuery && (
              <div className="absolute left-0 right-0 top-full mt-1 text-sm text-gray-500 bg-blue-50 px-3 py-2 rounded-lg border border-blue-200">
                Найдено задач: {filterTasksBySearch(tasks).length} из {tasks.length}
              </div>
            )}
          </div>
        </div>

        {/* Statistics */}
        {stats && <TaskStatsHeader stats={stats} />}

        {/* Filters */}
        {showFilters && (
          <TaskFilters
            filters={filters}
            onFilterChange={setFilters}
            onClose={() => setShowFilters(false)}
            employees={employees}
            projects={projects}
          />
        )}

        {/* Task View: Table or Kanban */}
        {loading ? (
          <div className="flex items-center justify-center h-96 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : viewMode === 'table' ? (
          /* Table View */
          <TaskTableView
            tasks={filterTasksBySearch(tasks)}
            onView={handleViewTask}
            onEdit={handleEditTask}
            onDelete={handleDeleteTask}
          />
        ) : (
          /* Kanban View */
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="overflow-x-auto">
              <div className="flex gap-4 min-w-max p-4">
                {Object.values(groupedTasks).map(({ employee, tasks: empTasks }) => (
                  <div
                    key={employee.id}
                    className={`flex-shrink-0 w-[340px] rounded-xl p-4 transition-all ${
                      dragOverColumn === employee.id
                        ? 'bg-blue-100 dark:bg-blue-900/30 ring-2 ring-blue-500 shadow-lg'
                        : 'bg-gray-50 dark:bg-gray-900/30'
                    }`}
                    onDragOver={handleDragOver(employee.id)}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop(employee.id)}
                  >
                    {/* Employee header */}
                    <div className="mb-4 pb-3 border-b border-gray-300 dark:border-gray-600">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow">
                          {(employee.first_name || employee.username).charAt(0).toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-bold text-base text-gray-900 dark:text-white truncate">
                            {employee.first_name && employee.last_name
                              ? `${employee.first_name} ${employee.last_name} (@${employee.username})`
                              : `@${employee.username}`}
                          </h3>
                          <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                            {employee.role === 'owner' ? 'Владелец' :
                             employee.role === 'admin' ? 'Администратор' :
                             employee.role === 'manager' ? 'Менеджер' : 'Исполнитель'}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <span className="px-2.5 py-1 bg-blue-500 text-white rounded-md font-semibold">
                          {empTasks.filter((t) => t.status === 'pending').length}
                        </span>
                        <span className="px-2.5 py-1 bg-yellow-500 text-white rounded-md font-semibold">
                          {empTasks.filter((t) => t.status === 'in_progress').length}
                        </span>
                        <span className="px-2.5 py-1 bg-green-500 text-white rounded-md font-semibold">
                          {empTasks.filter((t) => t.status === 'completed').length}
                        </span>
                      </div>
                    </div>

                    {/* Tasks */}
                    <div className="space-y-3 min-h-[200px]">
                      {empTasks.length === 0 ? (
                        <div className="text-center text-gray-400 py-8 bg-white dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600">
                          <p className="text-sm font-medium">Нет задач</p>
                        </div>
                      ) : (
                        empTasks.map((task) => (
                          <TaskCard
                            key={task.id}
                            task={task}
                            onView={() => handleViewTask(task)}
                            onEdit={() => handleEditTask(task)}
                            onDelete={() => handleDeleteTask(task.id)}
                            onStatusChange={(newStatus) =>
                              handleStatusChange(task.id, newStatus)
                            }
                            onDragStart={handleDragStart(task)}
                          />
                        ))
                      )}
                    </div>
                  </div>
                ))}

                {Object.keys(groupedTasks).length === 0 && (
                  <div className="w-full text-center py-12">
                    <p className="text-gray-400 dark:text-gray-500">Нет исполнителей с задачами</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      {showCreateModal && (
        <TaskCreateModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSuccess={handleCreateTask}
          employees={employees}
        />
      )}

      {showEditModal && selectedTask && (
        <TaskEditModal
          isOpen={showEditModal}
          onClose={() => {
            setShowEditModal(false)
            setSelectedTask(null)
          }}
          onSuccess={handleUpdateTask}
          task={selectedTask}
          employees={employees}
        />
      )}

      {showViewModal && selectedTask && (
        <TaskViewModal
          isOpen={showViewModal}
          onClose={() => {
            setShowViewModal(false)
            setSelectedTask(null)
          }}
          task={selectedTask}
          onEdit={() => {
            setShowViewModal(false)
            handleEditTask(selectedTask)
          }}
          onDelete={() => handleDeleteTask(selectedTask.id)}
          onRefresh={loadTasks}
        />
      )}

      {/* Toast Container */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </>
  )
}
