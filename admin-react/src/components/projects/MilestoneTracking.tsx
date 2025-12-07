import React, { useState, useEffect } from 'react'
import {
  Flag,
  CheckCircle,
  Circle,
  Calendar,
  Users,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  X,
  Plus,
  Edit2,
  Trash2,
  Clock,
  Target,
  BarChart3,
} from 'lucide-react'

interface MilestoneTrackingProps {
  projectId: number
  onClose: () => void
}

interface Milestone {
  id: number
  name: string
  description: string
  dueDate: string
  status: 'not-started' | 'in-progress' | 'completed' | 'delayed'
  progress: number // 0-100
  priority: 'low' | 'medium' | 'high' | 'critical'
  assignedTo: number[]
  assignedNames: string[]
  tasks: {
    total: number
    completed: number
  }
  budget: {
    allocated: number
    spent: number
  }
  dependencies: number[] // IDs других вех
  completedAt?: string
  deliverables: string[]
  notes: string
  createdAt: string
}

interface MilestoneTimeline {
  milestones: Milestone[]
  totalDuration: number
  criticalPath: number[]
}

const MilestoneTracking: React.FC<MilestoneTrackingProps> = ({ projectId, onClose }) => {
  const [milestones, setMilestones] = useState<Milestone[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingMilestone, setEditingMilestone] = useState<Milestone | null>(null)
  const [selectedMilestone, setSelectedMilestone] = useState<Milestone | null>(null)
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterPriority, setFilterPriority] = useState<string>('all')
  const [viewMode, setViewMode] = useState<'grid' | 'timeline' | 'gantt'>('grid')

  // Новая веха
  const [newMilestone, setNewMilestone] = useState({
    name: '',
    description: '',
    dueDate: '',
    priority: 'medium' as 'low' | 'medium' | 'high' | 'critical',
    assignedTo: [] as number[],
    deliverables: [] as string[],
    notes: '',
  })

  const [newDeliverable, setNewDeliverable] = useState('')

  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [])

  useEffect(() => {
    fetchMilestones()
  }, [projectId])

  const fetchMilestones = async () => {
    setLoading(true)
    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/milestones`, {
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      if (response.ok) {
        const data = await response.json()
        setMilestones(data)
      } else {
        // Mock data
        setMilestones([
          {
            id: 1,
            name: 'Завершение дизайна',
            description: 'Утверждение финального дизайна всех экранов',
            dueDate: '2024-03-15',
            status: 'completed',
            progress: 100,
            priority: 'high',
            assignedTo: [1, 2],
            assignedNames: ['Алексей Иванов', 'Мария Петрова'],
            tasks: { total: 12, completed: 12 },
            budget: { allocated: 15000, spent: 14500 },
            dependencies: [],
            completedAt: '2024-03-14',
            deliverables: ['Макеты всех страниц', 'UI Kit', 'Руководство по стилю'],
            notes: 'Завершено досрочно, клиент доволен',
            createdAt: '2024-02-01',
          },
          {
            id: 2,
            name: 'Разработка MVP',
            description: 'Базовая функциональность продукта',
            dueDate: '2024-04-01',
            status: 'in-progress',
            progress: 65,
            priority: 'critical',
            assignedTo: [1, 3, 4],
            assignedNames: ['Алексей Иванов', 'Дмитрий Смирнов', 'Елена Козлова'],
            tasks: { total: 28, completed: 18 },
            budget: { allocated: 45000, spent: 28000 },
            dependencies: [1],
            deliverables: ['Рабочее приложение', 'API документация', 'Тестовые данные'],
            notes: 'В процессе, некоторые задачи заблокированы',
            createdAt: '2024-02-15',
          },
          {
            id: 3,
            name: 'Тестирование и QA',
            description: 'Полное тестирование функциональности',
            dueDate: '2024-04-15',
            status: 'not-started',
            progress: 0,
            priority: 'high',
            assignedTo: [4],
            assignedNames: ['Елена Козлова'],
            tasks: { total: 15, completed: 0 },
            budget: { allocated: 12000, spent: 0 },
            dependencies: [2],
            deliverables: ['Отчет о тестировании', 'Список багов', 'Тестовые сценарии'],
            notes: 'Ожидает завершения разработки',
            createdAt: '2024-03-01',
          },
          {
            id: 4,
            name: 'Запуск бета-версии',
            description: 'Релиз для ограниченной группы пользователей',
            dueDate: '2024-04-25',
            status: 'not-started',
            progress: 0,
            priority: 'critical',
            assignedTo: [1, 2, 3, 4, 5],
            assignedNames: ['Алексей Иванов', 'Мария Петрова', 'Дмитрий Смирнов', 'Елена Козлова', 'Сергей Новиков'],
            tasks: { total: 10, completed: 0 },
            budget: { allocated: 8000, spent: 0 },
            dependencies: [2, 3],
            deliverables: ['Деплой на production', 'Мониторинг', 'Документация для пользователей'],
            notes: 'Требует завершения тестирования',
            createdAt: '2024-03-01',
          },
          {
            id: 5,
            name: 'Маркетинговая кампания',
            description: 'Запуск продвижения продукта',
            dueDate: '2024-03-20',
            status: 'delayed',
            progress: 40,
            priority: 'medium',
            assignedTo: [6],
            assignedNames: ['Маркетинговая команда'],
            tasks: { total: 8, completed: 3 },
            budget: { allocated: 25000, spent: 10000 },
            dependencies: [1],
            deliverables: ['Маркетинговый план', 'Контент для соцсетей', 'Пресс-релиз'],
            notes: 'Задержка из-за бюджетных ограничений',
            createdAt: '2024-02-20',
          },
        ])
      }
    } catch (error) {
      console.error('Error fetching milestones:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddMilestone = async () => {
    if (!newMilestone.name || !newMilestone.dueDate) {
      alert('Заполните название и дату')
      return
    }

    const milestoneData: Milestone = {
      ...newMilestone,
      id: Date.now(),
      status: 'not-started',
      progress: 0,
      assignedNames: [],
      tasks: { total: 0, completed: 0 },
      budget: { allocated: 0, spent: 0 },
      dependencies: [],
      createdAt: new Date().toISOString(),
    }

    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/milestones`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(milestoneData),
      })

      if (response.ok) {
        const data = await response.json()
        setMilestones([...milestones, data])
      } else {
        setMilestones([...milestones, milestoneData])
      }

      setShowAddModal(false)
      setNewMilestone({
        name: '',
        description: '',
        dueDate: '',
        priority: 'medium',
        assignedTo: [],
        deliverables: [],
        notes: '',
      })
    } catch (error) {
      console.error('Error adding milestone:', error)
    }
  }

  const handleUpdateMilestone = async (milestone: Milestone) => {
    try {
      const response = await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/milestones/${milestone.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
        body: JSON.stringify(milestone),
      })

      if (response.ok) {
        const data = await response.json()
        setMilestones(milestones.map((m) => (m.id === milestone.id ? data : m)))
      } else {
        setMilestones(milestones.map((m) => (m.id === milestone.id ? milestone : m)))
      }
    } catch (error) {
      console.error('Error updating milestone:', error)
    }
  }

  const handleDeleteMilestone = async (milestoneId: number) => {
    if (!confirm('Удалить веху?')) return

    try {
      await fetch(`http://147.45.215.199:8001/api/projects/${projectId}/milestones/${milestoneId}`, {
        method: 'DELETE',
        headers: {
          Authorization: 'Basic ' + btoa('admin:qwerty123'),
        },
      })
      setMilestones(milestones.filter((m) => m.id !== milestoneId))
    } catch (error) {
      console.error('Error deleting milestone:', error)
    }
  }

  const handleMarkComplete = async (milestone: Milestone) => {
    const updated = {
      ...milestone,
      status: 'completed' as const,
      progress: 100,
      completedAt: new Date().toISOString(),
    }
    await handleUpdateMilestone(updated)
  }

  const getStatusBadge = (status: string) => {
    const badges = {
      'not-started': { label: 'Не начата', color: 'bg-gray-100 text-gray-800', icon: Circle },
      'in-progress': { label: 'В работе', color: 'bg-blue-100 text-blue-800', icon: Clock },
      completed: { label: 'Завершена', color: 'bg-green-100 text-green-800', icon: CheckCircle },
      delayed: { label: 'Задержка', color: 'bg-red-100 text-red-800', icon: AlertTriangle },
    }
    return badges[status as keyof typeof badges] || badges['not-started']
  }

  const getPriorityBadge = (priority: string) => {
    const badges = {
      low: { label: 'Низкий', color: 'bg-gray-100 text-gray-700' },
      medium: { label: 'Средний', color: 'bg-blue-100 text-blue-700' },
      high: { label: 'Высокий', color: 'bg-orange-100 text-orange-700' },
      critical: { label: 'Критический', color: 'bg-red-100 text-red-700' },
    }
    return badges[priority as keyof typeof badges] || badges.medium
  }

  const getDaysUntilDue = (dueDate: string): number => {
    const due = new Date(dueDate)
    const today = new Date()
    const diff = due.getTime() - today.getTime()
    return Math.ceil(diff / (1000 * 60 * 60 * 24))
  }

  const isOverdue = (milestone: Milestone): boolean => {
    return milestone.status !== 'completed' && getDaysUntilDue(milestone.dueDate) < 0
  }

  const filteredMilestones = milestones.filter((milestone) => {
    const matchesStatus = filterStatus === 'all' || milestone.status === filterStatus
    const matchesPriority = filterPriority === 'all' || milestone.priority === filterPriority
    return matchesStatus && matchesPriority
  })

  const calculateStats = () => {
    const total = milestones.length
    const completed = milestones.filter((m) => m.status === 'completed').length
    const inProgress = milestones.filter((m) => m.status === 'in-progress').length
    const delayed = milestones.filter((m) => m.status === 'delayed').length
    const overdue = milestones.filter((m) => isOverdue(m)).length
    const avgProgress = milestones.length > 0 ? milestones.reduce((sum, m) => sum + m.progress, 0) / milestones.length : 0

    const totalBudget = milestones.reduce((sum, m) => sum + m.budget.allocated, 0)
    const spentBudget = milestones.reduce((sum, m) => sum + m.budget.spent, 0)

    return {
      total,
      completed,
      inProgress,
      delayed,
      overdue,
      avgProgress,
      totalBudget,
      spentBudget,
      budgetUsage: totalBudget > 0 ? (spentBudget / totalBudget) * 100 : 0,
    }
  }

  const stats = calculateStats()

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Загрузка вех...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-7xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Flag className="w-8 h-8" />
            <div>
              <h2 className="text-2xl font-bold">Отслеживание вех проекта</h2>
              <p className="text-indigo-100 text-sm">Проект #{projectId}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            aria-label="Закрыть"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4 p-6 bg-gray-50 border-b">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Flag className="w-4 h-4" />
              <span>Всего</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <CheckCircle className="w-4 h-4" />
              <span>Завершено</span>
            </div>
            <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Clock className="w-4 h-4" />
              <span>В работе</span>
            </div>
            <div className="text-2xl font-bold text-blue-600">{stats.inProgress}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <AlertTriangle className="w-4 h-4" />
              <span>Задержка</span>
            </div>
            <div className="text-2xl font-bold text-red-600">{stats.delayed}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Calendar className="w-4 h-4" />
              <span>Просрочено</span>
            </div>
            <div className="text-2xl font-bold text-orange-600">{stats.overdue}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Target className="w-4 h-4" />
              <span>Прогресс</span>
            </div>
            <div className="text-2xl font-bold text-purple-600">{stats.avgProgress.toFixed(0)}%</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <DollarSign className="w-4 h-4" />
              <span>Бюджет</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">${stats.totalBudget / 1000}k</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <BarChart3 className="w-4 h-4" />
              <span>Затрачено</span>
            </div>
            <div className="text-2xl font-bold text-blue-600">{stats.budgetUsage.toFixed(0)}%</div>
          </div>
        </div>

        {/* Filters and Actions */}
        <div className="flex flex-wrap justify-between items-center gap-4 p-6 bg-white border-b">
          <div className="flex flex-wrap gap-3">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">Все статусы</option>
              <option value="not-started">Не начата</option>
              <option value="in-progress">В работе</option>
              <option value="completed">Завершена</option>
              <option value="delayed">Задержка</option>
            </select>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="all">Все приоритеты</option>
              <option value="low">Низкий</option>
              <option value="medium">Средний</option>
              <option value="high">Высокий</option>
              <option value="critical">Критический</option>
            </select>
            <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`px-3 py-1 rounded transition-colors ${
                  viewMode === 'grid' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'
                }`}
              >
                Сетка
              </button>
              <button
                onClick={() => setViewMode('timeline')}
                className={`px-3 py-1 rounded transition-colors ${
                  viewMode === 'timeline' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'
                }`}
              >
                Таймлайн
              </button>
              <button
                onClick={() => setViewMode('gantt')}
                className={`px-3 py-1 rounded transition-colors ${
                  viewMode === 'gantt' ? 'bg-white shadow-sm' : 'hover:bg-gray-200'
                }`}
              >
                Гантт
              </button>
            </div>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Добавить веху
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {viewMode === 'grid' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {filteredMilestones.map((milestone) => {
                const statusBadge = getStatusBadge(milestone.status)
                const priorityBadge = getPriorityBadge(milestone.priority)
                const daysUntilDue = getDaysUntilDue(milestone.dueDate)
                const overdue = isOverdue(milestone)
                const StatusIcon = statusBadge.icon

                return (
                  <div
                    key={milestone.id}
                    className={`bg-white border-2 rounded-lg p-6 hover:shadow-lg transition-shadow ${
                      overdue ? 'border-red-300' : 'border-gray-200'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-start gap-3 flex-1">
                        <div
                          className={`w-10 h-10 rounded-full flex items-center justify-center ${
                            milestone.status === 'completed'
                              ? 'bg-green-100'
                              : milestone.status === 'in-progress'
                              ? 'bg-blue-100'
                              : milestone.status === 'delayed'
                              ? 'bg-red-100'
                              : 'bg-gray-100'
                          }`}
                        >
                          <StatusIcon
                            className={`w-6 h-6 ${
                              milestone.status === 'completed'
                                ? 'text-green-600'
                                : milestone.status === 'in-progress'
                                ? 'text-blue-600'
                                : milestone.status === 'delayed'
                                ? 'text-red-600'
                                : 'text-gray-600'
                            }`}
                          />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-bold text-lg text-gray-900 mb-2">{milestone.name}</h3>
                          <p className="text-sm text-gray-600 mb-3">{milestone.description}</p>
                          <div className="flex flex-wrap gap-2">
                            <span className={`text-xs px-2 py-1 rounded-full ${statusBadge.color}`}>
                              {statusBadge.label}
                            </span>
                            <span className={`text-xs px-2 py-1 rounded-full ${priorityBadge.color}`}>
                              {priorityBadge.label}
                            </span>
                            {overdue && (
                              <span className="text-xs px-2 py-1 rounded-full bg-red-100 text-red-800">
                                Просрочено на {Math.abs(daysUntilDue)} дн.
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setSelectedMilestone(milestone)}
                          className="p-1 text-gray-400 hover:text-indigo-600 transition-colors"
                          aria-label="Просмотр"
                        >
                          <Edit2 className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleDeleteMilestone(milestone.id)}
                          className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                          aria-label="Удалить"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {/* Progress */}
                      <div>
                        <div className="flex justify-between text-sm mb-2">
                          <span className="text-gray-600">Прогресс</span>
                          <span className="font-medium text-gray-900">{milestone.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div
                            className={`h-3 rounded-full transition-all ${
                              milestone.progress === 100
                                ? 'bg-green-500'
                                : milestone.progress >= 70
                                ? 'bg-blue-500'
                                : milestone.progress >= 40
                                ? 'bg-yellow-500'
                                : 'bg-red-500'
                            }`}
                            style={{ width: `${milestone.progress}%` }}
                          ></div>
                        </div>
                      </div>

                      {/* Stats Grid */}
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Срок сдачи</p>
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4 text-gray-400" />
                            <span className="text-sm font-medium text-gray-900">
                              {new Date(milestone.dueDate).toLocaleDateString('ru-RU')}
                            </span>
                          </div>
                          {!milestone.completedAt && (
                            <p
                              className={`text-xs ${
                                daysUntilDue < 0
                                  ? 'text-red-600'
                                  : daysUntilDue <= 7
                                  ? 'text-orange-600'
                                  : 'text-gray-500'
                              }`}
                            >
                              {daysUntilDue < 0
                                ? `Просрочено на ${Math.abs(daysUntilDue)} дн.`
                                : daysUntilDue === 0
                                ? 'Сегодня'
                                : `Осталось ${daysUntilDue} дн.`}
                            </p>
                          )}
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Команда</p>
                          <div className="flex items-center gap-1">
                            <Users className="w-4 h-4 text-gray-400" />
                            <span className="text-sm font-medium text-gray-900">{milestone.assignedNames.length}</span>
                          </div>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Задачи</p>
                          <p className="text-sm font-medium text-gray-900">
                            {milestone.tasks.completed} / {milestone.tasks.total}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Бюджет</p>
                          <div className="flex items-center gap-1">
                            <DollarSign className="w-4 h-4 text-gray-400" />
                            <span className="text-sm font-medium text-gray-900">
                              ${milestone.budget.spent}k / ${milestone.budget.allocated}k
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Deliverables */}
                      {milestone.deliverables.length > 0 && (
                        <div>
                          <p className="text-xs text-gray-500 mb-2">Результаты:</p>
                          <div className="flex flex-wrap gap-1">
                            {milestone.deliverables.map((deliverable, idx) => (
                              <span key={idx} className="text-xs px-2 py-1 bg-indigo-50 text-indigo-700 rounded">
                                {deliverable}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Actions */}
                      {milestone.status !== 'completed' && (
                        <div className="pt-4 border-t">
                          <button
                            onClick={() => handleMarkComplete(milestone)}
                            className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
                          >
                            <CheckCircle className="w-5 h-5" />
                            Отметить как завершенную
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          {viewMode === 'timeline' && (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="space-y-6">
                {filteredMilestones
                  .sort((a, b) => new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime())
                  .map((milestone, idx) => {
                    const statusBadge = getStatusBadge(milestone.status)
                    const priorityBadge = getPriorityBadge(milestone.priority)
                    const StatusIcon = statusBadge.icon

                    return (
                      <div key={milestone.id} className="flex gap-6">
                        <div className="flex flex-col items-center">
                          <div
                            className={`w-12 h-12 rounded-full flex items-center justify-center ${
                              milestone.status === 'completed'
                                ? 'bg-green-500'
                                : milestone.status === 'in-progress'
                                ? 'bg-blue-500'
                                : milestone.status === 'delayed'
                                ? 'bg-red-500'
                                : 'bg-gray-400'
                            }`}
                          >
                            <StatusIcon className="w-6 h-6 text-white" />
                          </div>
                          {idx < filteredMilestones.length - 1 && (
                            <div className="w-0.5 h-full bg-gray-300 flex-1 mt-2"></div>
                          )}
                        </div>
                        <div className="flex-1 pb-8">
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <h3 className="font-bold text-lg text-gray-900">{milestone.name}</h3>
                              <p className="text-sm text-gray-600">{milestone.description}</p>
                            </div>
                            <div className="flex flex-col items-end gap-2">
                              <span className={`text-xs px-2 py-1 rounded-full ${statusBadge.color}`}>
                                {statusBadge.label}
                              </span>
                              <span className={`text-xs px-2 py-1 rounded-full ${priorityBadge.color}`}>
                                {priorityBadge.label}
                              </span>
                            </div>
                          </div>
                          <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                            <div className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              <span>{new Date(milestone.dueDate).toLocaleDateString('ru-RU')}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Target className="w-4 h-4" />
                              <span>{milestone.progress}%</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Users className="w-4 h-4" />
                              <span>{milestone.assignedNames.length}</span>
                            </div>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                milestone.status === 'completed' ? 'bg-green-500' : 'bg-blue-500'
                              }`}
                              style={{ width: `${milestone.progress}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
              </div>
            </div>
          )}

          {viewMode === 'gantt' && (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="overflow-x-auto">
                <div className="min-w-[800px]">
                  <div className="grid grid-cols-12 gap-2 mb-4 text-xs text-gray-600 font-medium">
                    <div className="col-span-3">Веха</div>
                    <div className="col-span-9 grid grid-cols-12 text-center">
                      <div>Янв</div>
                      <div>Фев</div>
                      <div>Мар</div>
                      <div>Апр</div>
                      <div>Май</div>
                      <div>Июн</div>
                      <div>Июл</div>
                      <div>Авг</div>
                      <div>Сен</div>
                      <div>Окт</div>
                      <div>Ноя</div>
                      <div>Дек</div>
                    </div>
                  </div>
                  {filteredMilestones.map((milestone) => {
                    const month = new Date(milestone.dueDate).getMonth()
                    return (
                      <div key={milestone.id} className="grid grid-cols-12 gap-2 mb-3">
                        <div className="col-span-3">
                          <p className="text-sm font-medium text-gray-900 truncate">{milestone.name}</p>
                          <p className="text-xs text-gray-500">{milestone.progress}%</p>
                        </div>
                        <div className="col-span-9 grid grid-cols-12 gap-1">
                          {Array.from({ length: 12 }).map((_, idx) => (
                            <div
                              key={idx}
                              className={`h-8 rounded ${
                                idx === month
                                  ? milestone.status === 'completed'
                                    ? 'bg-green-500'
                                    : milestone.status === 'in-progress'
                                    ? 'bg-blue-500'
                                    : milestone.status === 'delayed'
                                    ? 'bg-red-500'
                                    : 'bg-gray-400'
                                  : 'bg-gray-100'
                              }`}
                            ></div>
                          ))}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          )}

          {filteredMilestones.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <Flag className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>Нет вех, соответствующих фильтрам</p>
            </div>
          )}
        </div>

        {/* Add Modal */}
        {showAddModal && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
              <h3 className="text-xl font-bold mb-4">Добавить веху</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Название *</label>
                  <input
                    type="text"
                    value={newMilestone.name}
                    onChange={(e) => setNewMilestone({ ...newMilestone, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="Название вехи"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Описание</label>
                  <textarea
                    value={newMilestone.description}
                    onChange={(e) => setNewMilestone({ ...newMilestone, description: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="Описание вехи"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Срок сдачи *</label>
                    <input
                      type="date"
                      value={newMilestone.dueDate}
                      onChange={(e) => setNewMilestone({ ...newMilestone, dueDate: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Приоритет</label>
                    <select
                      value={newMilestone.priority}
                      onChange={(e) =>
                        setNewMilestone({
                          ...newMilestone,
                          priority: e.target.value as 'low' | 'medium' | 'high' | 'critical',
                        })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    >
                      <option value="low">Низкий</option>
                      <option value="medium">Средний</option>
                      <option value="high">Высокий</option>
                      <option value="critical">Критический</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Результаты</label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={newDeliverable}
                      onChange={(e) => setNewDeliverable(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && newDeliverable) {
                          setNewMilestone({
                            ...newMilestone,
                            deliverables: [...newMilestone.deliverables, newDeliverable],
                          })
                          setNewDeliverable('')
                        }
                      }}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      placeholder="Добавить результат (Enter для добавления)"
                    />
                    <button
                      onClick={() => {
                        if (newDeliverable) {
                          setNewMilestone({
                            ...newMilestone,
                            deliverables: [...newMilestone.deliverables, newDeliverable],
                          })
                          setNewDeliverable('')
                        }
                      }}
                      className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                      <Plus className="w-5 h-5" />
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {newMilestone.deliverables.map((deliverable, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center gap-1 text-sm px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full"
                      >
                        {deliverable}
                        <button
                          onClick={() =>
                            setNewMilestone({
                              ...newMilestone,
                              deliverables: newMilestone.deliverables.filter((_, i) => i !== idx),
                            })
                          }
                          className="hover:text-indigo-900"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Примечания</label>
                  <textarea
                    value={newMilestone.notes}
                    onChange={(e) => setNewMilestone({ ...newMilestone, notes: e.target.value })}
                    rows={2}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="Дополнительные заметки"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Отмена
                </button>
                <button
                  onClick={handleAddMilestone}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  Добавить
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Detail Modal */}
        {selectedMilestone && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-6 w-full max-w-3xl max-h-[80vh] overflow-y-auto">
              <div className="flex justify-between items-start mb-6">
                <h3 className="text-2xl font-bold text-gray-900">{selectedMilestone.name}</h3>
                <button
                  onClick={() => setSelectedMilestone(null)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              <div className="space-y-6">
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Описание:</p>
                  <p className="text-gray-900">{selectedMilestone.description}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Статус:</p>
                    <span className={`text-xs px-3 py-1 rounded-full ${getStatusBadge(selectedMilestone.status).color}`}>
                      {getStatusBadge(selectedMilestone.status).label}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Приоритет:</p>
                    <span
                      className={`text-xs px-3 py-1 rounded-full ${getPriorityBadge(selectedMilestone.priority).color}`}
                    >
                      {getPriorityBadge(selectedMilestone.priority).label}
                    </span>
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Прогресс: {selectedMilestone.progress}%</p>
                  <div className="w-full bg-gray-200 rounded-full h-4">
                    <div
                      className="bg-indigo-600 h-4 rounded-full transition-all"
                      style={{ width: `${selectedMilestone.progress}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Команда:</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedMilestone.assignedNames.map((name, idx) => (
                      <span key={idx} className="text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded-full">
                        {name}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Результаты:</p>
                  <ul className="list-disc list-inside space-y-1">
                    {selectedMilestone.deliverables.map((deliverable, idx) => (
                      <li key={idx} className="text-gray-900">
                        {deliverable}
                      </li>
                    ))}
                  </ul>
                </div>
                {selectedMilestone.notes && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Примечания:</p>
                    <p className="text-gray-900 bg-gray-50 p-4 rounded-lg">{selectedMilestone.notes}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default MilestoneTracking
