import { useState, useEffect } from 'react'
import {
  X,
  Network,
  ChevronRight,
  ChevronDown,
  Link as LinkIcon,
  Unlink,
  Plus,
  AlertCircle,
  CheckCircle,
  Clock,
  Target,
} from 'lucide-react'

interface Task {
  id: number
  title: string
  status: string
  assignee?: string
  deadline?: string
  dependencies: number[]
  blockedBy: number[]
}

interface DependencyRelation {
  fromTask: number
  toTask: number
  type: 'blocks' | 'requires'
}

interface TaskDependencyMapProps {
  isOpen: boolean
  onClose: () => void
  projectId: number | null
  projectName: string
}

export const TaskDependencyMap = ({
  isOpen,
  onClose,
  projectId,
  projectName,
}: TaskDependencyMapProps) => {
  const [tasks, setTasks] = useState<Task[]>([])
  const [dependencies, setDependencies] = useState<DependencyRelation[]>([])
  const [expandedTasks, setExpandedTasks] = useState<Set<number>>(new Set())
  const [selectedTask, setSelectedTask] = useState<number | null>(null)
  const [isAddingDependency, setIsAddingDependency] = useState(false)
  const [newDependency, setNewDependency] = useState({
    fromTask: 0,
    toTask: 0,
    type: 'blocks' as const,
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen && projectId) {
      loadTasksAndDependencies()
    }
  }, [isOpen, projectId])

  useEffect(() => {
    if (isOpen) {
      const scrollY = window.scrollY
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'
      document.body.style.overflow = 'hidden'
    } else {
      const scrollY = document.body.style.top
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      document.body.style.overflow = ''
      window.scrollTo(0, parseInt(scrollY || '0') * -1)
    }
  }, [isOpen])

  const loadTasksAndDependencies = async () => {
    if (!projectId) return

    setLoading(true)
    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/task-dependencies`,
        {
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setTasks(data.tasks || [])
        setDependencies(data.dependencies || [])
      } else {
        // Mock data
        setTasks([
          {
            id: 1,
            title: 'Разработка архитектуры',
            status: 'completed',
            assignee: 'Иван',
            deadline: '2025-02-01',
            dependencies: [],
            blockedBy: [],
          },
          {
            id: 2,
            title: 'Дизайн интерфейса',
            status: 'completed',
            assignee: 'Мария',
            deadline: '2025-02-05',
            dependencies: [],
            blockedBy: [],
          },
          {
            id: 3,
            title: 'Реализация бэкенда',
            status: 'in_progress',
            assignee: 'Алексей',
            deadline: '2025-02-15',
            dependencies: [1],
            blockedBy: [],
          },
          {
            id: 4,
            title: 'Реализация фронтенда',
            status: 'in_progress',
            assignee: 'Елена',
            deadline: '2025-02-20',
            dependencies: [2],
            blockedBy: [],
          },
          {
            id: 5,
            title: 'Интеграция фронтенда и бэкенда',
            status: 'pending',
            assignee: 'Сергей',
            deadline: '2025-02-25',
            dependencies: [3, 4],
            blockedBy: [],
          },
          {
            id: 6,
            title: 'Тестирование',
            status: 'pending',
            assignee: 'Ольга',
            deadline: '2025-03-01',
            dependencies: [5],
            blockedBy: [],
          },
          {
            id: 7,
            title: 'Исправление багов',
            status: 'pending',
            deadline: '2025-03-05',
            dependencies: [6],
            blockedBy: [],
          },
          {
            id: 8,
            title: 'Деплой',
            status: 'pending',
            assignee: 'Иван',
            deadline: '2025-03-10',
            dependencies: [7],
            blockedBy: [],
          },
        ])

        setDependencies([
          { fromTask: 1, toTask: 3, type: 'blocks' },
          { fromTask: 2, toTask: 4, type: 'blocks' },
          { fromTask: 3, toTask: 5, type: 'blocks' },
          { fromTask: 4, toTask: 5, type: 'blocks' },
          { fromTask: 5, toTask: 6, type: 'blocks' },
          { fromTask: 6, toTask: 7, type: 'blocks' },
          { fromTask: 7, toTask: 8, type: 'blocks' },
        ])
      }
    } catch (err) {
      console.error('Error loading dependencies:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddDependency = async () => {
    if (!newDependency.fromTask || !newDependency.toTask) return
    if (newDependency.fromTask === newDependency.toTask) {
      alert('Задача не может зависеть от самой себя')
      return
    }

    // Check for circular dependencies
    if (wouldCreateCircularDependency(newDependency.fromTask, newDependency.toTask)) {
      alert('Это создаст циклическую зависимость!')
      return
    }

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/task-dependencies`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
          body: JSON.stringify(newDependency),
        }
      )

      if (response.ok) {
        setNewDependency({ fromTask: 0, toTask: 0, type: 'blocks' })
        setIsAddingDependency(false)
        await loadTasksAndDependencies()
      }
    } catch (err) {
      console.error('Error adding dependency:', err)
    }
  }

  const handleRemoveDependency = async (fromTask: number, toTask: number) => {
    if (!confirm('Удалить эту зависимость?')) return

    try {
      const response = await fetch(
        `http://localhost:8001/admin/api/projects/${projectId}/task-dependencies/${fromTask}/${toTask}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: 'Basic ' + btoa('admin:qwerty123'),
          },
        }
      )

      if (response.ok) {
        await loadTasksAndDependencies()
      }
    } catch (err) {
      console.error('Error removing dependency:', err)
    }
  }

  const wouldCreateCircularDependency = (fromId: number, toId: number): boolean => {
    // Simple check: if toId already depends on fromId (directly or indirectly)
    const visited = new Set<number>()
    const queue = [toId]

    while (queue.length > 0) {
      const current = queue.shift()!
      if (current === fromId) return true
      if (visited.has(current)) continue

      visited.add(current)
      const task = tasks.find((t) => t.id === current)
      if (task) {
        queue.push(...task.dependencies)
      }
    }

    return false
  }

  const toggleTaskExpanded = (taskId: number) => {
    const newExpanded = new Set(expandedTasks)
    if (newExpanded.has(taskId)) {
      newExpanded.delete(taskId)
    } else {
      newExpanded.add(taskId)
    }
    setExpandedTasks(newExpanded)
  }

  const getTaskById = (id: number): Task | undefined => {
    return tasks.find((t) => t.id === id)
  }

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-700 border-green-300'
      case 'in_progress':
        return 'bg-blue-100 text-blue-700 border-blue-300'
      case 'pending':
        return 'bg-gray-100 text-gray-700 border-gray-300'
      case 'blocked':
        return 'bg-red-100 text-red-700 border-red-300'
      default:
        return 'bg-gray-100 text-gray-700 border-gray-300'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4" />
      case 'in_progress':
        return <Clock className="w-4 h-4" />
      case 'pending':
        return <Target className="w-4 h-4" />
      case 'blocked':
        return <AlertCircle className="w-4 h-4" />
      default:
        return <Target className="w-4 h-4" />
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'short',
    }).format(date)
  }

  const getCriticalPath = (): number[] => {
    // Simple critical path calculation (longest path)
    const visited = new Set<number>()
    const paths: number[][] = []

    const findPaths = (taskId: number, currentPath: number[]) => {
      if (visited.has(taskId)) return
      visited.add(taskId)

      const task = getTaskById(taskId)
      if (!task) return

      const newPath = [...currentPath, taskId]

      const dependents = tasks.filter((t) => t.dependencies.includes(taskId))
      if (dependents.length === 0) {
        paths.push(newPath)
      } else {
        dependents.forEach((dep) => findPaths(dep.id, newPath))
      }

      visited.delete(taskId)
    }

    // Start from tasks with no dependencies
    tasks
      .filter((t) => t.dependencies.length === 0)
      .forEach((t) => findPaths(t.id, []))

    // Find longest path
    const longestPath = paths.reduce((longest, current) =>
      current.length > longest.length ? current : longest
    , [])

    return longestPath
  }

  if (!isOpen) return null

  const criticalPath = getCriticalPath()
  const blockedTasks = tasks.filter((t) =>
    t.dependencies.some((depId) => {
      const dep = getTaskById(depId)
      return dep && dep.status !== 'completed'
    })
  )

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <Network className="w-6 h-6" />
            <div>
              <h3 className="text-xl font-bold">Карта зависимостей задач</h3>
              <p className="text-purple-100 text-sm mt-1">{projectName}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Stats */}
        <div className="px-6 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <Network className="w-4 h-4 text-gray-600" />
              <span className="text-gray-600">Всего задач:</span>
              <span className="font-bold text-purple-600">{tasks.length}</span>
            </div>
            <div className="flex items-center gap-2">
              <LinkIcon className="w-4 h-4 text-blue-600" />
              <span className="text-gray-600">Зависимостей:</span>
              <span className="font-bold text-blue-600">{dependencies.length}</span>
            </div>
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-orange-600" />
              <span className="text-gray-600">Заблокировано:</span>
              <span className="font-bold text-orange-600">{blockedTasks.length}</span>
            </div>
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-red-600" />
              <span className="text-gray-600">Критический путь:</span>
              <span className="font-bold text-red-600">{criticalPath.length} задач</span>
            </div>
          </div>

          {!isAddingDependency && (
            <button
              onClick={() => setIsAddingDependency(true)}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-semibold text-sm"
            >
              <Plus className="w-4 h-4" />
              Добавить зависимость
            </button>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Add Dependency Form */}
          {isAddingDependency && (
            <div className="mb-6 bg-purple-50 border-2 border-purple-200 rounded-xl p-4">
              <h4 className="font-bold text-gray-900 mb-4">Добавить зависимость</h4>

              <div className="grid grid-cols-3 gap-3 items-end">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Задача (блокирует)
                  </label>
                  <select
                    value={newDependency.fromTask}
                    onChange={(e) =>
                      setNewDependency({ ...newDependency, fromTask: Number(e.target.value) })
                    }
                    className="w-full px-4 py-2 border-2 border-purple-300 rounded-lg focus:border-purple-500 outline-none"
                  >
                    <option value={0}>Выберите задачу</option>
                    {tasks.map((task) => (
                      <option key={task.id} value={task.id}>
                        {task.title}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="text-center text-2xl text-purple-600 font-bold">→</div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Задача (зависит)
                  </label>
                  <select
                    value={newDependency.toTask}
                    onChange={(e) =>
                      setNewDependency({ ...newDependency, toTask: Number(e.target.value) })
                    }
                    className="w-full px-4 py-2 border-2 border-purple-300 rounded-lg focus:border-purple-500 outline-none"
                  >
                    <option value={0}>Выберите задачу</option>
                    {tasks.map((task) => (
                      <option key={task.id} value={task.id}>
                        {task.title}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex gap-2 mt-4">
                <button
                  onClick={handleAddDependency}
                  disabled={!newDependency.fromTask || !newDependency.toTask}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 font-semibold"
                >
                  <LinkIcon className="w-4 h-4" />
                  Создать зависимость
                </button>
                <button
                  onClick={() => {
                    setIsAddingDependency(false)
                    setNewDependency({ fromTask: 0, toTask: 0, type: 'blocks' })
                  }}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-semibold"
                >
                  Отмена
                </button>
              </div>
            </div>
          )}

          {/* Critical Path Highlight */}
          {criticalPath.length > 0 && (
            <div className="mb-6 bg-red-50 border-2 border-red-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <Target className="w-5 h-5 text-red-600" />
                <h4 className="font-bold text-gray-900">Критический путь</h4>
              </div>
              <div className="flex flex-wrap gap-2">
                {criticalPath.map((taskId, index) => {
                  const task = getTaskById(taskId)
                  if (!task) return null

                  return (
                    <div key={taskId} className="flex items-center gap-2">
                      <span className="px-3 py-1 bg-red-100 text-red-700 rounded-lg text-sm font-semibold border-2 border-red-300">
                        {task.title}
                      </span>
                      {index < criticalPath.length - 1 && (
                        <ChevronRight className="w-4 h-4 text-red-400" />
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Tasks List with Dependencies */}
          {loading ? (
            <div className="text-center py-12 text-gray-500">Загрузка...</div>
          ) : tasks.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Network className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-lg font-semibold">Нет задач в проекте</p>
            </div>
          ) : (
            <div className="space-y-3">
              {tasks.map((task) => {
                const isExpanded = expandedTasks.has(task.id)
                const dependsOn = task.dependencies.map(getTaskById).filter(Boolean) as Task[]
                const blocks = tasks.filter((t) => t.dependencies.includes(task.id))
                const isOnCriticalPath = criticalPath.includes(task.id)
                const isBlocked = task.dependencies.some((depId) => {
                  const dep = getTaskById(depId)
                  return dep && dep.status !== 'completed'
                })

                return (
                  <div
                    key={task.id}
                    className={`bg-white border-2 rounded-xl transition-all ${
                      isOnCriticalPath
                        ? 'border-red-400 shadow-lg'
                        : isBlocked
                          ? 'border-orange-400'
                          : 'border-gray-200 hover:border-purple-400'
                    }`}
                  >
                    {/* Task Header */}
                    <div
                      className={`p-4 cursor-pointer ${isOnCriticalPath ? 'bg-red-50' : isBlocked ? 'bg-orange-50' : 'hover:bg-gray-50'}`}
                      onClick={() => toggleTaskExpanded(task.id)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3 flex-1">
                          {isExpanded ? (
                            <ChevronDown className="w-5 h-5 text-gray-500 mt-0.5" />
                          ) : (
                            <ChevronRight className="w-5 h-5 text-gray-500 mt-0.5" />
                          )}

                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h5 className="font-bold text-gray-900 text-lg">{task.title}</h5>
                              {isOnCriticalPath && (
                                <span className="px-2 py-0.5 bg-red-500 text-white rounded-full text-xs font-bold">
                                  Критический путь
                                </span>
                              )}
                              {isBlocked && (
                                <span className="px-2 py-0.5 bg-orange-500 text-white rounded-full text-xs font-bold">
                                  Заблокирована
                                </span>
                              )}
                            </div>

                            <div className="flex flex-wrap gap-2 items-center">
                              <span
                                className={`px-3 py-1 rounded-full text-xs font-semibold border-2 flex items-center gap-1 ${getStatusColor(
                                  task.status
                                )}`}
                              >
                                {getStatusIcon(task.status)}
                                {task.status}
                              </span>

                              {task.assignee && (
                                <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-semibold">
                                  {task.assignee}
                                </span>
                              )}

                              {task.deadline && (
                                <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-semibold">
                                  {formatDate(task.deadline)}
                                </span>
                              )}

                              <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-semibold">
                                {dependsOn.length} зависимостей
                              </span>

                              <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-semibold">
                                Блокирует: {blocks.length}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Expanded Details */}
                    {isExpanded && (
                      <div className="p-4 border-t border-gray-200 bg-gray-50 space-y-4">
                        {/* Dependencies */}
                        {dependsOn.length > 0 && (
                          <div>
                            <h6 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                              <LinkIcon className="w-4 h-4" />
                              Зависит от:
                            </h6>
                            <div className="space-y-2">
                              {dependsOn.map((dep) => (
                                <div
                                  key={dep.id}
                                  className="flex items-center justify-between bg-white rounded-lg p-3 border border-gray-200"
                                >
                                  <div className="flex items-center gap-3">
                                    <span
                                      className={`px-2 py-1 rounded text-xs font-semibold ${getStatusColor(
                                        dep.status
                                      )}`}
                                    >
                                      {dep.status}
                                    </span>
                                    <span className="text-sm font-semibold text-gray-900">
                                      {dep.title}
                                    </span>
                                  </div>
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      handleRemoveDependency(dep.id, task.id)
                                    }}
                                    className="p-1 text-red-600 hover:bg-red-100 rounded transition-colors"
                                    title="Удалить зависимость"
                                  >
                                    <Unlink className="w-4 h-4" />
                                  </button>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Blocks */}
                        {blocks.length > 0 && (
                          <div>
                            <h6 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                              <AlertCircle className="w-4 h-4" />
                              Блокирует:
                            </h6>
                            <div className="space-y-2">
                              {blocks.map((blockedTask) => (
                                <div
                                  key={blockedTask.id}
                                  className="flex items-center justify-between bg-white rounded-lg p-3 border border-gray-200"
                                >
                                  <div className="flex items-center gap-3">
                                    <span
                                      className={`px-2 py-1 rounded text-xs font-semibold ${getStatusColor(
                                        blockedTask.status
                                      )}`}
                                    >
                                      {blockedTask.status}
                                    </span>
                                    <span className="text-sm font-semibold text-gray-900">
                                      {blockedTask.title}
                                    </span>
                                  </div>
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      handleRemoveDependency(task.id, blockedTask.id)
                                    }}
                                    className="p-1 text-red-600 hover:bg-red-100 rounded transition-colors"
                                    title="Удалить зависимость"
                                  >
                                    <Unlink className="w-4 h-4" />
                                  </button>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center flex-shrink-0">
          <div className="text-sm text-gray-600">
            <AlertCircle className="w-4 h-4 inline mr-1" />
            Критический путь показывает самую длинную цепочку зависимостей
          </div>
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all font-semibold"
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  )
}
